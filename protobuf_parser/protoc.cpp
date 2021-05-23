// Python version of this module of this is called _protobuf_parser

#include <pybind11/pybind11.h>
#include <google/protobuf/compiler/command_line_interface.h>
#include <vector>
#include <tuple>

namespace py = pybind11;

struct Error {};
struct SyntaxError : Error {};
struct Warning : Error {};


std::tuple<const char, std::vector<Error>> parse(py::args files) {
    vector<Error> vect;

    std::tuple<const char, std::vector<Error>> ret = ('d', vect);

    return ret;

}

//std::vector<Error> run(py::args args, py::kwargs kwargs) {
//    std::vector
//}

PYBIND11_MODULE(_protobuf_parser, m) {
    m.doc() = "Raw bindings for protoc";

    py::class_<Error>(m, "Error");
    py::class_<SyntaxError>(m, "SyntaxError");
    py::class_<Warning>(m, "Warning");
    py::def('parse', &parser, "");
}
