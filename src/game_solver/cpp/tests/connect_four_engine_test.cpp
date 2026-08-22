#include "connect_four_engine.hpp"

#include <cassert>
#include <stdexcept>
#include <vector>

int main() {
    using game_solver::ColumnHeights;
    using game_solver::legal_columns;

    assert(legal_columns(ColumnHeights{}) ==
           (std::vector<int>{0, 1, 2, 3, 4, 5, 6}));
    assert(legal_columns(ColumnHeights{6, 0, 6, 5, 6, 6, 1}) ==
           (std::vector<int>{1, 3, 6}));

    bool rejected_invalid_height = false;
    try {
        (void)legal_columns(ColumnHeights{0, 0, 0, 7, 0, 0, 0});
    } catch (const std::invalid_argument&) {
        rejected_invalid_height = true;
    }
    assert(rejected_invalid_height);
}
