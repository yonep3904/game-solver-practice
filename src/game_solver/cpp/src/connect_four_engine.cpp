#include "connect_four_engine.hpp"

#include <vector>
#include <cstddef>
#include <stdexcept>

namespace game_solver {

std::vector<int> legal_columns(const ColumnHeights& heights) {
    std::vector<int> result;
    for (std::size_t column = 0; column < heights.size(); ++column) {
        if (heights[column] < 0 ||
            heights[column] > static_cast<int>(connect_four_rows)) {
            throw std::invalid_argument("column height must be between 0 and 6");
        }
        if (heights[column] < static_cast<int>(connect_four_rows)) {
            result.push_back(static_cast<int>(column));
        }
    }
    return result;
}

}  // namespace game_solver
