#include <tuple>
#include <vector>

#include <google/protobuf/compiler/command_line_interface.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


namespace py = pybind11;

struct Error {};
struct SyntaxError : Error {};
struct Warning : Error {};


std::tuple<py::bytes, std::vector<Error>> parse(py::args files) {
    std::vector<Error> vect;
    std::string str;
    return std::make_tuple(py::bytes(str), vect);
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
