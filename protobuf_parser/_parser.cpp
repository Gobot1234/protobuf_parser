#include <tuple>
#include <vector>

#include <google/protobuf/compiler/command_line_interface.h>
#include <google/protobuf/compiler/importer.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <google/protobuf/descriptor.h>
#include <google/protobuf/io/tokenizer.h>


namespace py = pybind11;
namespace compiler = google::protobuf::compiler;
namespace io = google::protobuf::io;

class Error {
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


class NullErrorCollector : public io::ErrorCollector {  // for actual parsing
    void AddError(int line, int column, const std::string &message) override {}
    void AddWarning(int line, int column, const std::string &message) override {}
};


class ErrorCollector : public compiler::MultiFileErrorCollector {  // this one actually does stuff
    public:
        std::vector<Error> errors;

        void AddError(const std::string &filename, int line, int column, const std::string &message) override {
            errors.emplace_back(filename, line, column, message);
        }

        void AddWarning(const std::string &filename, int line, int column, const std::string &message) override {
            errors.emplace_back(filename, line, column, message);
        }

        ErrorCollector() {
            errors = std::vector<Error>();
        }
};


class SourceTree : public compiler::SourceTree {
    public:
        py::list files;

        io::ArrayInputStream *Open(const std::string &filename) override {
            for (auto file : files)  // would be nice to use a dict instead of a linear search, but for now this is fine
                if (py::cast<std::string>(file.attr("name")) == filename) {
                    auto bytes = py::cast<std::string>(file.attr("read")());
                    return new io::ArrayInputStream(&bytes, bytes.length());
                }
        }

        explicit SourceTree(const py::list &files_) {
            files = files_;
        }
};


auto parse(const py::list &files) {
    std::vector<google::protobuf::FileDescriptorProto *> proto_files;

    // currently we have to parse twice, this isn't great, but is currently the best thing I've worked out
    ErrorCollector error_collector;
    SourceTree tree(files);
    compiler::Importer importer(&tree, &error_collector);

    for (auto file : files) {
        importer.Import(py::cast<std::string>(file.attr("name")));
    }

    if (!error_collector.errors.empty()) {
        return py::make_tuple(py::list(), error_collector.errors);
    }

    NullErrorCollector null_error_collector;
    compiler::Parser parser;
    parser.RecordErrorsTo(&null_error_collector);

    for (auto file : files) {
        google::protobuf::FileDescriptorProto* proto_file = nullptr;
        auto bytes = py::cast<std::string>(file.attr("read")());
        std::unique_ptr<io::ZeroCopyInputStream> input(new io::ArrayInputStream(&bytes, bytes.length()));
        io::Tokenizer tokenizer(input.get(), &null_error_collector);
        parser.Parse(&tokenizer, proto_file);
        proto_files.push_back(proto_file);
    }

    auto bytes = py::list();

    for (auto proto_file : proto_files) {
        bytes.append(py::bytes(proto_file->SerializeAsString()));
    }

    return py::make_tuple(bytes, py::list());
}

//std::vector<Error> run(py::args args, py::kwargs kwargs) {
//    std::vector
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
