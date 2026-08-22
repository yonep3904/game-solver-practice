#pragma once

#include <array>
#include <cstddef>
#include <vector>

namespace game_solver {

inline constexpr std::size_t connect_four_columns = 7;
inline constexpr std::size_t connect_four_rows = 6;

using ColumnHeights = std::array<int, connect_four_columns>;

// Return the columns which still have room for another piece.
std::vector<int> legal_columns(const ColumnHeights& heights);

}  // namespace game_solver
