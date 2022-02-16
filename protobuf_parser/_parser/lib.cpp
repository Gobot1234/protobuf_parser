// Copyright (c) James Hilton-Balfe under the MIT License see LICENSE

#include "errors.cpp"
#include "parse.cpp"
#include "run.cpp"

PYBIND11_MODULE(_parser, m) {
    m.doc() = "Raw bindings for protoc";

    py::class_<Error>(m, "Error")
        .def_readonly("filename", &Error::filename)
        .def_readonly("line", &Error::line)
        .def_readonly("column", &Error::column)
        .def_readonly("message", &Error::message)
        .def_readonly("warning", &Error::warning);
    m.def("parse", parse, "");
    m.def("run", run, "");
}
