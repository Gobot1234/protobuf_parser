#include <google/protobuf/compiler/command_line_interface.h>
#include <google/protobuf/compiler/importer.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <google/protobuf/descriptor.h>
#include <google/protobuf/io/tokenizer.h>


namespace py = pybind11;
namespace compiler = google::protobuf::compiler;
namespace io = google::protobuf::io;

class Error {  // TODO: make this inherit from Exception
    public:
        std::string filename;
        int line;
        int column;
        std::string message;

    Error(const std::string& filename_,int line_, int column_, const std::string &message_) {
        filename = filename_;
        line = line_;
        column = column_;
        message = message_;
    }
};


class ErrorCollector : public google::protobuf::DescriptorPool::ErrorCollector, public io::ErrorCollector {
    public:
        std::vector<Error> errors;
        std::string current_filename;

        // parsing errors
        void AddError(int line, int column, const std::string &message) override {
            errors.emplace_back(current_filename, line + 1, column + 1, message);
        }
        void AddWarning(int line, int column, const std::string &message) override {
            errors.emplace_back(current_filename, line + 1, column + 1, message);
        }

        // conversion errors
        void AddError(
            const std::string& filename,
            const std::string& element_name,
            const google::protobuf::Message* descriptor,
            ErrorLocation location,
            const std::string& message
        ) override {
            errors.emplace_back(filename, -1, -1, message);
        }

        void AddWarning(
            const std::string& filename,
            const std::string& element_name,
            const google::protobuf::Message* descriptor,
            ErrorLocation location,
            const std::string& message
        ) override {
            errors.emplace_back(filename, -1, -1, message);
        }

        ErrorCollector() {
            errors = std::vector<Error>();
            current_filename = std::string();
        }
};


auto parse(const py::list &files) {
    std::vector<google::protobuf::FileDescriptorProto> proto_files;

    ErrorCollector error_collector;
    compiler::Parser parser;
    google::protobuf::DescriptorPool pool;

    for (auto file : files) {
        google::protobuf::FileDescriptorProto proto_file;

        auto bytes = file.attr("read")().cast<std::string>();
        auto name = error_collector.current_filename = file.attr("name").cast<std::string>();
        io::ArrayInputStream input(bytes.c_str(), bytes.size());

        io::Tokenizer tokenizer(&input, &error_collector);
        parser.Parse(&tokenizer, &proto_file);  // TODO: catch libprotobuf WARNING google/protobuf/compiler/parser.cc:651
        proto_file.set_name(name.c_str());
        pool.BuildFileCollectingErrors(proto_file, &error_collector);
        proto_files.push_back(proto_file);
    }

    auto bytes = py::list();

    if (error_collector.errors.empty()) {
        for (const auto &proto_file : proto_files) {
            bytes.append(py::bytes(proto_file.SerializeAsString()));
        }
    }

    return py::make_tuple(bytes, error_collector.errors);
}


//auto run(py::args args, py::kwargs kwargs) {
//    compiler::CommandLineInterface cli;
//    ErrorCollector error_collector;
//
//    cli.ParseArguments();
//    return error_collector.errors;
//}

PYBIND11_MODULE(_parser, m) {
    m.doc() = "Raw bindings for protoc";

    py::class_<Error>(m, "Error")
        .def_readwrite("filename", &Error::filename)  // TODO: read only?
        .def_readwrite("line", &Error::line)
        .def_readwrite("column", &Error::column)
        .def_readwrite("message", &Error::message);
    m.def("parse", &parse, "");
}
