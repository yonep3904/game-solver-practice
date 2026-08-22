#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <algorithm>
#include <vector>

#include "connect_four_engine.hpp"

namespace py = pybind11;

namespace {

py::typing::List<int> legal_columns(py::typing::Iterable<int> heights) {
    std::vector<int> values;
    for (const py::handle height : heights) {
        values.push_back(py::cast<int>(height));
    }
    if (values.size() != game_solver::connect_four_columns) {
        throw py::value_error("heights must contain exactly 7 values");
    }

    game_solver::ColumnHeights fixed_heights{};
    std::copy(values.begin(), values.end(), fixed_heights.begin());

    py::typing::List<int> result;
    for (const int column : game_solver::legal_columns(fixed_heights)) {
        result.append(column);
    }
    return result;
}

}  // namespace

PYBIND11_MODULE(_core, module) {
    module.doc() = "C++ acceleration for game_solver";
    module.def("legal_columns", &legal_columns, py::arg("heights"));
}
