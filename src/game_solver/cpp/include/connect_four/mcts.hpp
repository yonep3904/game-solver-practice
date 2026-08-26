#pragma once

#include <cstddef>
#include <cstdint>

#include "connect_four/engine.hpp"

namespace connect_four {

[[nodiscard]]
EngineAction mcts(const EngineState& state, std::size_t simulations, double exploration_weight,
                  std::uint64_t seed);

}  // namespace connect_four
