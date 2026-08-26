#include "connect_four/engine.hpp"

#include <cstdint>
#include <optional>
#include <stdexcept>

namespace connect_four {

LegalActions Engine::legal_actions(const EngineState& state) noexcept {
    LegalActions result{};

    if (is_terminal(state)) {
        return result;
    }

    for (std::uint8_t column = 0; column < BOARD_WIDTH; ++column) {
        if ((state.mask & TOP_MASKS[column]) == 0) {
            result.actions[result.size_++] = column;
        }
    }

    return result;
}

EngineState Engine::apply_action(const EngineState& state, const EngineAction action) {
    if (action >= BOARD_WIDTH) {
        throw std::out_of_range{"connect_four: action is outside the board"};
    }

    if (is_terminal(state)) {
        throw std::logic_error{"connect_four: cannot play from a terminal position"};
    }

    if ((state.mask & TOP_MASKS[action]) != 0) {
        throw std::logic_error{"connect_four: column is full"};
    }

    return apply_action_unchecked(state, action);
}

bool Engine::is_terminal(const EngineState& state) noexcept {
    return terminal_value(state).has_value();
}

std::optional<float> Engine::terminal_value(const EngineState& state) noexcept {
    if (has_won(state.opponent())) {
        return -1.0F;
    }

    if (state.mask == FULL_MASK) {
        return 0.0F;
    }

    return std::nullopt;
}

}  // namespace connect_four
