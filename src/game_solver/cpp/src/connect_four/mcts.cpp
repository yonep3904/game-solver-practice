#include "connect_four/mcts.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <random>
#include <stdexcept>
#include <vector>

namespace connect_four {
namespace {

using NodeIndex = std::size_t;
inline constexpr NodeIndex NO_NODE = std::numeric_limits<NodeIndex>::max();

struct Node {
    EngineState state;
    NodeIndex parent{NO_NODE};
    EngineAction action{};
    std::array<NodeIndex, BOARD_WIDTH> children{};
    std::array<EngineAction, BOARD_WIDTH> untried_actions{};
    std::uint8_t child_count{};
    std::uint8_t untried_count{};
    // Sum of outcomes from state.current_player's perspective.
    double value_sum{};
    std::size_t visit_count{};
};

[[nodiscard]]
Node make_node(const EngineState& state, const NodeIndex parent, const EngineAction action,
               std::mt19937_64& generator) {
    Node node{.state = state, .parent = parent, .action = action};
    if (Engine::is_terminal(state)) {
        return node;
    }
    for (std::uint8_t column = 0; column < BOARD_WIDTH; ++column) {
        if ((state.mask & TOP_MASKS[column]) == 0) {
            node.untried_actions[node.untried_count++] = column;
        }
    }
    std::shuffle(node.untried_actions.begin(), node.untried_actions.begin() + node.untried_count,
                 generator);
    return node;
}

[[nodiscard]]
double uct(const Node& child, const double log_parent_visits,
           const double exploration_weight) noexcept {
    // Selection only sees children already visited by expansion/backpropagation.
    const double visits = static_cast<double>(child.visit_count);
    return -child.value_sum / visits + exploration_weight * std::sqrt(log_parent_visits / visits);
}

[[nodiscard]]
NodeIndex select_node(const std::vector<Node>& nodes, NodeIndex current,
                      const double exploration_weight) noexcept {
    while (!Engine::is_terminal(nodes[current].state) && nodes[current].untried_count == 0) {
        const Node& parent = nodes[current];
        const double log_parent_visits = std::log(static_cast<double>(parent.visit_count));
        NodeIndex best = parent.children[0];
        double best_value = uct(nodes[best], log_parent_visits, exploration_weight);
        for (std::uint8_t i = 1; i < parent.child_count; ++i) {
            const NodeIndex candidate = parent.children[i];
            const double candidate_value =
                uct(nodes[candidate], log_parent_visits, exploration_weight);
            if (candidate_value > best_value) {
                best = candidate;
                best_value = candidate_value;
            }
        }
        current = best;
    }
    return current;
}

[[nodiscard]]
double simulate(EngineState state, std::mt19937_64& generator) noexcept {
    double perspective = 1.0;
    for (;;) {
        if (const auto value = Engine::terminal_value(state)) {
            return perspective * static_cast<double>(*value);
        }

        std::array<EngineAction, BOARD_WIDTH> actions{};
        std::uint8_t count = 0;
        for (std::uint8_t column = 0; column < BOARD_WIDTH; ++column) {
            if ((state.mask & TOP_MASKS[column]) == 0) {
                actions[count++] = column;
            }
        }
        std::uniform_int_distribution<unsigned int> distribution(0, count - 1);
        state = Engine::apply_action_unchecked(state, actions[distribution(generator)]);
        perspective = -perspective;
    }
}

void backpropagate(std::vector<Node>& nodes, NodeIndex current, double score) noexcept {
    while (current != NO_NODE) {
        Node& node = nodes[current];
        ++node.visit_count;
        node.value_sum += score;
        score = -score;
        current = node.parent;
    }
}

}  // namespace

EngineAction mcts(const EngineState& state, const std::size_t simulations,
                  const double exploration_weight, const std::uint64_t seed) {
    if (simulations == 0) {
        throw std::invalid_argument{"connect_four: simulations must be positive"};
    }
    if (!(exploration_weight >= 0.0)) {
        throw std::invalid_argument{"connect_four: exploration_weight must be non-negative"};
    }
    if (Engine::legal_actions(state).empty()) {
        throw std::invalid_argument{"No legal actions available."};
    }

    std::mt19937_64 generator(seed);
    std::vector<Node> nodes;
    nodes.reserve(simulations + 1);
    nodes.push_back(make_node(state, NO_NODE, 0, generator));

    for (std::size_t iteration = 0; iteration < simulations; ++iteration) {
        NodeIndex current = select_node(nodes, 0, exploration_weight);
        if (nodes[current].untried_count != 0) {
            Node& parent = nodes[current];
            const EngineAction action = parent.untried_actions[--parent.untried_count];
            const EngineState next_state = Engine::apply_action_unchecked(parent.state, action);
            const NodeIndex child = nodes.size();
            nodes.push_back(make_node(next_state, current, action, generator));
            nodes[current].children[nodes[current].child_count++] = child;
            current = child;
        }
        backpropagate(nodes, current, simulate(nodes[current].state, generator));
    }

    const Node& root = nodes[0];
    NodeIndex best = root.children[0];
    for (std::uint8_t i = 1; i < root.child_count; ++i) {
        const NodeIndex candidate = root.children[i];
        if (nodes[candidate].visit_count > nodes[best].visit_count) {
            best = candidate;
        }
    }
    return nodes[best].action;
}

}  // namespace connect_four
