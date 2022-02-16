// Copyright 2016 gRPC authors under the Apache License, Version 2.0 see LICENSE
// Includes a lot of
// https://github.com/grpc/grpc/blob/master/tools/distrib/python/grpcio_tools/grpc_tools/main.cc
//
// Copyright (c) James Hilton-Balfe under the MIT License see LICENSE

#include <google/protobuf/compiler/code_generator.h>
#include <google/protobuf/compiler/command_line_interface.h>
#include <google/protobuf/compiler/python/python_generator.h>
#include <pybind11/pybind11.h>

#include "errors.cpp"

namespace py = pybind11;
namespace compiler = google::protobuf::compiler;
namespace io = google::protobuf::io;

void calculate_transitive_closure(const google::protobuf::FileDescriptor* descriptor,
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
    GeneratorContextImpl(const std::vector<const google::protobuf::FileDescriptor*>& parsed_files,
                         std::vector<std::pair<std::string, std::string>> files_out)
        : files_(files_out), parsed_files_(parsed_files) {}

    io::ZeroCopyOutputStream* Open(const std::string& filename) {
        files_.emplace_back(filename, "");
        return new io::StringOutputStream(&(files_.back().second));
    }

    io::ZeroCopyOutputStream* OpenForAppend(const std::string& filename) { return Open(filename); }

    io::ZeroCopyOutputStream* OpenForInsert(const std::string& filename, const std::string& insertion_point) {
        return Open(filename);
    }

    void ListParsedFiles(std::vector<const ::google::protobuf::FileDescriptor*>* output) { *output = parsed_files_; }

   private:
    std::vector<std::pair<std::string, std::string>> files_;
    const std::vector<const google::protobuf::FileDescriptor*>& parsed_files_;
};

auto run(const std::string& protobuf_path,
         const std::vector<std::string>& include_paths,
         const std::vector<std::pair<std::string, std::string>>& files_out) {
    std::cout << ("maade it to c");
    compiler::python::Generator code_generator;
    std::unique_ptr<ErrorCollector> error_collector(new ErrorCollector());
    std::unique_ptr<compiler::DiskSourceTree> source_tree(new compiler::DiskSourceTree());
    std::cout << ("maade it this far");
    for (const auto& include_path : include_paths) {
        source_tree->MapPath("", include_path);
    }
    std::cout << ("a it this far");
    compiler::Importer importer(source_tree.get(), error_collector.get());
    const google::protobuf::FileDescriptor* parsed_file = importer.Import(protobuf_path);
    std::vector<const google::protobuf::FileDescriptor*> transitive_closure;
    std::unordered_set<const google::protobuf::FileDescriptor*> visited;
    std::cout << ("EVEN further far");
    calculate_transitive_closure(parsed_file, &transitive_closure, &visited);
    std::cout << ("trans closure it this far");
    GeneratorContextImpl generator_context(transitive_closure, files_out);
    std::string error;

    for (const auto descriptor : transitive_closure) {
        code_generator.Generate(descriptor, "", &generator_context, &error);
    }
    std::cout << ("generated");

    return error_collector.get()->errors;
}
