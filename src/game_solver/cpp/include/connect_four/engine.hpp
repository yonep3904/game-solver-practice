#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace connect_four {

inline constexpr int BOARD_WIDTH = 7;
inline constexpr int BOARD_HEIGHT = 6;
inline constexpr int CELL_COUNT = BOARD_WIDTH * BOARD_HEIGHT;
inline constexpr int STRIDE = BOARD_HEIGHT + 1;

using Bitboard = std::uint64_t;

static_assert(BOARD_WIDTH * STRIDE <= 64);

namespace detail {

consteval auto make_bottom_masks() {
    std::array<Bitboard, BOARD_WIDTH> result{};

    for (int column = 0; column < BOARD_WIDTH; ++column) {
        result[column] = Bitboard{1} << (column * STRIDE);
    }

    return result;
}

consteval auto make_top_masks() {
    std::array<Bitboard, BOARD_WIDTH> result{};

    for (int column = 0; column < BOARD_WIDTH; ++column) {
        result[column] = Bitboard{1} << (column * STRIDE + BOARD_HEIGHT - 1);
    }

    return result;
}

consteval auto make_column_masks() {
    std::array<Bitboard, BOARD_WIDTH> result{};

    constexpr Bitboard column_mask = (Bitboard{1} << BOARD_HEIGHT) - 1;

    for (int column = 0; column < BOARD_WIDTH; ++column) {
        result[column] = column_mask << (column * STRIDE);
    }

    return result;
}

consteval auto make_full_mask() {
    Bitboard result = 0;

    constexpr auto column_masks = detail::make_column_masks();

    for (const Bitboard mask : column_masks) {
        result |= mask;
    }

    return result;
}

}  // namespace detail

inline constexpr auto BOTTOM_MASKS = detail::make_bottom_masks();
inline constexpr auto TOP_MASKS = detail::make_top_masks();
inline constexpr auto COLUMN_MASKS = detail::make_column_masks();
inline constexpr auto FULL_MASK = detail::make_full_mask();

struct EngineState {
    // Stones belonging to the player whose turn it is.
    Bitboard position{};

    // Stones belonging to either player.
    Bitboard mask{};

    [[nodiscard]]
    constexpr Bitboard opponent() const noexcept {
        return mask ^ position;
    }
};

using EngineAction = std::uint8_t;

struct LegalActions {
    std::array<EngineAction, BOARD_WIDTH> actions{};
    std::uint8_t size_{};

    [[nodiscard]]
    constexpr auto begin() const noexcept {
        return actions.begin();
    }

    [[nodiscard]]
    constexpr auto end() const noexcept {
        return actions.begin() + size_;
    }

    [[nodiscard]]
    constexpr bool empty() const noexcept {
        return size_ == 0;
    }

    [[nodiscard]]
    constexpr std::size_t size() const noexcept {
        return size_;
    }

    [[nodiscard]]
    constexpr EngineAction operator[](std::size_t index) const noexcept {
        return actions[index];
    }
};

class Engine {
   public:
    [[nodiscard]]
    static constexpr EngineState initial_state() noexcept {
        return {};
    }

    [[nodiscard]]
    static LegalActions legal_actions(const EngineState& state) noexcept;

    [[nodiscard]]
    static EngineState apply_action(const EngineState& state, EngineAction action);

    [[nodiscard]]
    static bool is_terminal(const EngineState& state) noexcept;

    [[nodiscard]]
    static std::optional<float> terminal_value(const EngineState& state) noexcept;

    // ホットパスはヘッダファイルに書く

    [[nodiscard]]
    static EngineState apply_action_unchecked(const EngineState& state,
                                              const EngineAction action) noexcept {
        const Bitboard move = (state.mask + BOTTOM_MASKS[action]) & COLUMN_MASKS[action];

        return {
            .position = state.opponent(),
            .mask = state.mask | move,
        };
    }

    [[nodiscard]]
    static bool has_won(const Bitboard bits) noexcept {
        // Vertical
        {
            constexpr int shift = 1;
            const Bitboard pair = bits & (bits >> shift);

            if ((pair & (pair >> (2 * shift))) != 0) {
                return true;
            }
        }

        // Horizontal
        {
            constexpr int shift = STRIDE;
            const Bitboard pair = bits & (bits >> shift);

            if ((pair & (pair >> (2 * shift))) != 0) {
                return true;
            }
        }

        // Diagonal /
        {
            constexpr int shift = STRIDE - 1;
            const Bitboard pair = bits & (bits >> shift);

            if ((pair & (pair >> (2 * shift))) != 0) {
                return true;
            }
        }

        // Diagonal backslash
        {
            constexpr int shift = STRIDE + 1;
            const Bitboard pair = bits & (bits >> shift);

            if ((pair & (pair >> (2 * shift))) != 0) {
                return true;
            }
        }

        return false;
    }
};

}  // namespace connect_four
