#include <tuple>
#include <vector>

#include <google/protobuf/compiler/command_line_interface.h>
#include <google/protobuf/compiler/importer.h>
#include <google/protobuf/descriptor.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


namespace py = pybind11;


class Error {};
class SyntaxError : Error {};
class Warning : Error {};

// class ErrorReturner : MultiFileErrorCollector {
//     ErrorPrinter(ErrorFormat format, DiskSourceTree* tree = NULL): 
//         format_(format),
//         tree_(tree),
//         found_errors_(false),
//         found_warnings_(false),
//         std::vector<Error> errors;
//         errors_(errors),  // warnings also live here
//         files_(py::object),
//         {},
// };

// class FileTree : SourceTree {
//     public: 
//         map<std::string, py::object> files;
//     io::ZeroCopyInputStream* Open(const std::string& filename) {
//         return
//     }
// };


// class CoolDescriptorPool : DescriptorPool {

// }


std::tuple<py::bytes, std::vector<Error>> parse(py::args files) {
    std::vector<Error> errors;
    std::string result;
    // std::vector<const FileDescriptor> parsed_files;
    // result.append("hello");
    // py::print(files);

    // SourceTree source_tree;

    // g = (new DescriptorBuilder()).BuildFile();
    // *Importer importer = new Importer();
    // importer.Import(file);

    // std::vector<std::string> *new_files = files.cast();
    // for (auto i : new_files)
    //     std::cout << i << ' ';

    return std::make_tuple(py::bytes(result), errors);
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
