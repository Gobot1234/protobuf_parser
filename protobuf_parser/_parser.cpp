#include <tuple>
#include <vector>
#include <unordered_map>

#include <google/protobuf/compiler/command_line_interface.h>
#include <google/protobuf/compiler/importer.h>
#include <google/protobuf/descriptor.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


namespace py = pybind11;


class Error {
    public:
        std::string filename;
        int line;
        int column;
        std::string message;

    Error(
        std::string filename_,
        int line_,
        int column_,
        std::string message_,
    ) {
        filename = filename_;
        line = line_;
        column = column_;
        message = message_;
    }
};


class ErrorCollector : MultiFileErrorCollector {
    std::vector<Error> errors;

    ErrorReturner() {
        errors = std::vector<Error>();
    }

    void AddError(
        const std::string &filename,
        int line,
        int column,
        const std::string &message,
    ) {
        Error error = Error(filename, line, column, message);
        errors.push_back(error);
    }

    void AddWarning(
        const std::string &filename,
        int line,
        int column,
        const std::string &message,
    ) {
        Error error = Error(filename, line, column, message);
        errors.push_back(error);
    }
};

typedef FileMapping = unordered_map<std::string, py::object>;

class FileTree : SourceTree {
    public:
        FileMapping files;

    FileTree(FileMapping files_) {
        files = files_;
    }

    ArrayInputStream Open(const std::string &filename) {
        py::object file = files[filename];
        auto bytes = py::cast<std::string>(file.attr("read")());
        auto size = bytes.length();
        return ArrayInputStream(&bytes, size, 8192);
    }
};


auto parse(FileMapping files) {
    std::vector<Error> errors;
    std::string result;
    // std::vector<const FileDescriptor> parsed_files;
    // result.append("hello");
    // py::print(files);

    // SourceTree source_tree;

    // g = (new DescriptorBuilder()).BuildFile();
    Importer importer = new Importer(FileTree(files), ErrorCollector());
    // auto descriptor = importer.Import(file);

    return py::make_tuple(py::bytes(result), errors);
}

//std::vector<Error> run(py::args args, py::kwargs kwargs) {
//    std::vector
//}

PYBIND11_MODULE(_parser, m) {
    m.doc() = "Raw bindings for protoc";

    py::class_<Error>(m, "Error");
    py::class_<SyntaxError>(m, "SyntaxError");
    py::class_<Warning>(m, "Warning");
    m.def("parse", &parse, "");
}
