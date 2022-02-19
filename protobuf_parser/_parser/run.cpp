// Copyright 2016 gRPC authors under the Apache License, Version 2.0 see LICENSE
// Includes a lot of
// https://github.com/grpc/grpc/blob/master/tools/distrib/python/grpcio_tools/grpc_tools/main.cc
//
// Copyright (c) James Hilton-Balfe under the MIT License see LICENSE

#include <google/protobuf/compiler/code_generator.h>
#include <google/protobuf/compiler/command_line_interface.h>
#include <google/protobuf/compiler/python/python_generator.h>
#include <pybind11/pybind11.h>
#include <fstream>
#include <iostream>
using namespace std;

#include "errors.cpp"

namespace py = pybind11;
namespace compiler = google::protobuf::compiler;
namespace io = google::protobuf::io;

static void calculate_transitive_closure(const google::protobuf::FileDescriptor* descriptor,
                                         std::vector<const google::protobuf::FileDescriptor*>* transitive_closure,
                                         std::unordered_set<const google::protobuf::FileDescriptor*>* visited) {
    for (int i = 0; i < descriptor->dependency_count(); ++i) {
        const google::protobuf::FileDescriptor* dependency = descriptor->dependency(i);
        if (visited->find(dependency) == visited->end()) {
            calculate_transitive_closure(dependency, transitive_closure, visited);
        }
    }
    transitive_closure->push_back(descriptor);
    visited->insert(descriptor);
}

class GeneratorContextImpl : public compiler::GeneratorContext {
   public:
    std::vector<std::pair<std::string, std::string>> files;
    const std::vector<const google::protobuf::FileDescriptor*>& parsed_files;

    GeneratorContextImpl(const std::vector<const google::protobuf::FileDescriptor*>& parsed_files_,
                         std::vector<std::pair<std::string, std::string>> files_)
        : files(files_), parsed_files(parsed_files_) {}

    io::ZeroCopyOutputStream* Open(const std::string& filename) {
        files.emplace_back(filename, "");
        return new io::StringOutputStream(&(files.back().second));
    }

    io::ZeroCopyOutputStream* OpenForAppend(const std::string& filename) { return Open(filename); }

    io::ZeroCopyOutputStream* OpenForInsert(const std::string& filename, const std::string& insertion_point) {
        return Open(filename);
    }

    void ListParsedFiles(std::vector<const ::google::protobuf::FileDescriptor*>* output) { *output = parsed_files; }
};

auto run(const std::vector<std::string>& protobuf_paths, const std::vector<std::string>& include_paths) {
    compiler::python::Generator code_generator;
    std::unique_ptr<ErrorCollector> error_collector(new ErrorCollector());
    std::unique_ptr<compiler::DiskSourceTree> source_tree(new compiler::DiskSourceTree());
    std::vector<std::pair<std::string, std::string>> files_out;

    for (const auto& include_path : include_paths) {
        source_tree->MapPath("", include_path);
    }

    compiler::Importer importer(source_tree.get(), error_collector.get());
    std::vector<const google::protobuf::FileDescriptor*> parsed_files;

    for (auto& protobuf_path : protobuf_paths) {
        auto parsed_file = importer.Import(protobuf_path);
        if (parsed_file == nullptr) {
            auto filename = protobuf_path.substr(protobuf_path.find_last_of("/\\") + 1);
            files_out.emplace_back(filename, "");
            return py::make_tuple(files_out, error_collector.get()->errors);
        }
        parsed_files.push_back(parsed_file);
    }

    std::vector<const google::protobuf::FileDescriptor*> transitive_closure;
    std::unordered_set<const google::protobuf::FileDescriptor*> visited;
    for (const auto parsed_file : parsed_files) {
        calculate_transitive_closure(parsed_file, &transitive_closure, &visited);
    }

    GeneratorContextImpl generator_context(transitive_closure, files_out);
    std::string error;

    for (const auto descriptor : transitive_closure) {
        code_generator.Generate(descriptor, "", &generator_context, &error);
    }

    return py::make_tuple(generator_context.files, error_collector.get()->errors);
}
