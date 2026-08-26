#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cstddef>
#include <cstdint>

#include "connect_four/mcts.hpp"
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
    m.def(
        "connect_four_mcts_cpp",
        [](std::uint64_t position, std::uint64_t mask, std::size_t simulations,
           double exploration_weight, std::uint64_t seed) {
            return connect_four::mcts({position, mask}, simulations, exploration_weight, seed);
        },
        py::arg("position"), py::arg("mask"), py::arg("simulations"), py::arg("exploration_weight"),
        py::arg("seed"), py::call_guard<py::gil_scoped_release>());
}
