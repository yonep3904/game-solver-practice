#include "connect_four/mcts.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <random>
#include <span>
#include <stdexcept>
#include <vector>

#include "connect_four/engine.hpp"

namespace connect_four {
namespace {

using NodeIndex = std::size_t;
constexpr auto NO_NODE = std::numeric_limits<NodeIndex>::max();

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

    [[nodiscard]]
    auto children_view() const noexcept {
        return std::span{children}.first(child_count);
    }

    [[nodiscard]]
    auto untried_actions_view() noexcept {
        return std::span{untried_actions}.first(untried_count);
    }
};

using RandomGenerator = std::mt19937_64;

[[nodiscard]]
Node make_node(const EngineState& state, const NodeIndex parent, const EngineAction action,
               RandomGenerator& generator) {
    Node node{.state = state, .parent = parent, .action = action};

    const auto legal_actions = Engine::legal_actions(state);
    node.untried_count = static_cast<std::uint8_t>(legal_actions.size());
    std::ranges::copy(legal_actions, node.untried_actions.begin());
    std::ranges::shuffle(node.untried_actions_view(), generator);

    return node;
}

[[nodiscard]]
double uct(const Node& child, const double log_parent_visits,
           const double exploration_weight) noexcept {
    const auto visits = static_cast<double>(child.visit_count);
    const auto exploitation = -child.value_sum / visits;
    const auto exploration = exploration_weight * std::sqrt(log_parent_visits / visits);

    return exploitation + exploration;
}

[[nodiscard]]
NodeIndex select_child(const std::vector<Node>& nodes, const Node& parent,
                       const double exploration_weight) noexcept {
    const auto log_parent_visits = std::log(static_cast<double>(parent.visit_count));
    const auto children = parent.children_view();

    auto best = children.front();
    auto best_value = uct(nodes[best], log_parent_visits, exploration_weight);

    // ホットパスなので STL を使わずにループする
    for (std::size_t i = 1; i < children.size(); ++i) {
        const auto candidate = children[i];
        const auto candidate_value = uct(nodes[candidate], log_parent_visits, exploration_weight);
        if (candidate_value > best_value) {
            best = candidate;
            best_value = candidate_value;
        }
    }

    return best;
}

[[nodiscard]]
NodeIndex select_node(const std::vector<Node>& nodes, NodeIndex current,
                      const double exploration_weight) noexcept {
    for (;;) {
        const auto& node = nodes[current];
        if (node.untried_count != 0 || Engine::is_terminal(node.state)) {
            return current;
        }
        current = select_child(nodes, node, exploration_weight);
    }
}

[[nodiscard]]
NodeIndex expand(std::vector<Node>& nodes, const NodeIndex parent_index,
                 RandomGenerator& generator) {
    // 絶対に push_back() の前に参照を取らない:
    // push_back() によって vector が再割り当てされる可能性あり
    auto& parent = nodes[parent_index];
    const auto action = parent.untried_actions[--parent.untried_count];
    const auto next_state = Engine::apply_action_unchecked(parent.state, action);
    const auto child_index = nodes.size();

    nodes.push_back(make_node(next_state, parent_index, action, generator));
    nodes[parent_index].children[nodes[parent_index].child_count++] = child_index;

    return child_index;
}

[[nodiscard]]
double simulate(EngineState state, RandomGenerator& generator) noexcept {
    auto perspective = 1.0;

    for (;;) {
        if (const auto value = Engine::terminal_value(state)) {
            return perspective * static_cast<double>(*value);
        }

        // ホットパスなので終局判定まで行う Engine::legal_actions を呼ばずに自前で合法手を列挙
        std::array<EngineAction, BOARD_WIDTH> actions{};
        std::uint8_t action_count = 0;
        for (std::uint8_t column = 0; column < BOARD_WIDTH; ++column) {
            if ((state.mask & TOP_MASKS[column]) == 0) {
                actions[action_count++] = column;
            }
        }

        std::uniform_int_distribution<unsigned int> distribution{0, action_count - 1U};
        const auto action = actions[distribution(generator)];
        state = Engine::apply_action_unchecked(state, action);
        perspective = -perspective;
    }
}

void backpropagate(std::vector<Node>& nodes, NodeIndex current, double score) noexcept {
    while (current != NO_NODE) {
        auto& node = nodes[current];
        ++node.visit_count;
        node.value_sum += score;

        score = -score;
        current = node.parent;
    }
}

[[nodiscard]]
EngineAction most_visited_action(const std::vector<Node>& nodes) noexcept {
    const auto& root = nodes.front();
    const auto children = root.children_view();

    const auto best = std::ranges::max_element(
        children, {}, [&](const NodeIndex index) { return nodes[index].visit_count; });
    return nodes[*best].action;
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
        throw std::invalid_argument{"connect_four: no legal actions available"};
    }

    RandomGenerator generator{seed};
    std::vector<Node> nodes;
    nodes.reserve(simulations + 1);
    nodes.push_back(make_node(state, NO_NODE, EngineAction{}, generator));

    for (std::size_t iteration = 0; iteration < simulations; ++iteration) {
        auto current = select_node(nodes, 0, exploration_weight);
        if (nodes[current].untried_count != 0) {
            current = expand(nodes, current, generator);
        }

        const auto score = simulate(nodes[current].state, generator);
        backpropagate(nodes, current, score);
    }

    return most_visited_action(nodes);
}

}  // namespace connect_four
