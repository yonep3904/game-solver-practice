#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "sample.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = "C++ acceleration for game_solver";

    // Sample functions and classes
    m.def("_sample_add", &sample::add, py::arg("a"), py::arg("b"));

    m.def("_sample_double_values", &sample::double_values, py::arg("values"));

    py::class_<sample::Counter>(m, "_SampleCounter")
        .def(py::init<int>(), py::arg("initial_value") = 0)
        .def("increment", &sample::Counter::increment)
        .def("add", &sample::Counter::add, py::arg("value"))
        .def_property_readonly("value", &sample::Counter::value)
        .def("message", &sample::Counter::message);

    // Game solver
}
