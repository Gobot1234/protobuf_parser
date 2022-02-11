// Copyright (c) James Hilton-Balfe under the MIT License see LICENSE

#include <google/protobuf/compiler/command_line_interface.h>
#include <google/protobuf/compiler/importer.h>
#include <google/protobuf/descriptor.h>
#include <google/protobuf/io/tokenizer.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "errors.cpp"

namespace py = pybind11;
namespace compiler = google::protobuf::compiler;
namespace io = google::protobuf::io;

auto parse(const py::list& files) {
    std::vector<google::protobuf::FileDescriptorProto> proto_files;

    ErrorCollector error_collector;
    compiler::Parser parser;
    parser.RecordErrorsTo(&error_collector);
    google::protobuf::DescriptorPool pool;

    for (auto file : files) {
        google::protobuf::FileDescriptorProto proto_file;

        auto bytes = file.attr("read")().cast<std::string>();
        auto name = error_collector.current_filename =
            file.attr("name").cast<std::string>();
        proto_file.set_name(name.c_str());

        io::ArrayInputStream input(bytes.c_str(), bytes.size());
        io::Tokenizer tokenizer(&input, &error_collector);

        parser.Parse(&tokenizer, &proto_file);
        pool.BuildFileCollectingErrors(proto_file, &error_collector);
        proto_files.push_back(proto_file);
    }

    auto bytes = py::list();

    if (!error_collector.has_errors) {
        for (const auto& proto_file : proto_files) {
            bytes.append(py::bytes(proto_file.SerializeAsString()));
        }
    }

    return py::make_tuple(bytes, error_collector.errors);
}
