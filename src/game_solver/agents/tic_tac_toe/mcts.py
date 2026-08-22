from __future__ import annotations

import math
import random

from game_solver.core import Player
from game_solver.games.tic_tac_toe import (
    TicTacToeAction,
    TicTacToeAgent,
    TicTacToeGameRules,
    TicTacToeState,
)
from game_solver.utils import argmax


class _MCTSNode:
    def __init__(
        self,
        state: TicTacToeState,
        parent: _MCTSNode | None = None,
        action: TicTacToeAction | None = None,
    ):
        self.state = state
        self.parent = parent
        self.action = action

        self.children: list[_MCTSNode] = []
        self.untried_actions: list[TicTacToeAction] = []

        self.visits = 0
        self.value = 0.0


class TicTacToeMCTSAgent(TicTacToeAgent):
    """UCT を用いた Monte Carlo Tree Search Agent。"""

    def __init__(
        self,
        simulations: int = 1000,
        exploration_weight: float = math.sqrt(2.0),
        seed: int | None = None,
    ) -> None:
        if simulations <= 0:
            raise ValueError("simulations must be positive")
        if exploration_weight < 0:
            raise ValueError("exploration_weight must be non-negative")

        self.simulations = simulations
        self.exploration_weight = exploration_weight

        self._rules = TicTacToeGameRules()
        self._rg = random.Random(seed)

    def select_action(self, state: TicTacToeState) -> TicTacToeAction:
        actions = self._rules.legal_actions(state)

        if not actions:
            raise ValueError("No legal actions available.")

        root_player = self._rules.current_player(state)

        root = self._make_node(state)

        for _ in range(self.simulations):
            node = root

            # 1. Selection
            while not self._rules.is_terminal(node.state) and not node.untried_actions:
                node = self._select_child(node, root_player)

            # 2. Expansion
            if not self._rules.is_terminal(node.state) and node.untried_actions:
                node = self._expand(node)

            # 3. Simulation
            score = self._playout(node.state, root_player)

            # 4. Backpropagation
            self._backpropagate(node, score)

        # 最終的な手の選択では exploration は不要。
        # 最も多く探索された子を選ぶ。
        visits = [child.visits for child in root.children]
        return root.children[argmax(visits)].action

    def _make_node(
        self,
        state: TicTacToeState,
        parent: _MCTSNode | None = None,
        action: TicTacToeAction | None = None,
    ) -> _MCTSNode:
        node = _MCTSNode(
            state=state,
            parent=parent,
            action=action,
        )
        node.untried_actions = list(self._rules.legal_actions(state))
        self._rg.shuffle(node.untried_actions)

        return node

    def _select_child(
        self,
        node: _MCTSNode,
        root_player: Player,
    ) -> _MCTSNode:
        """UCT 値が最大の子ノードを選択する。"""

        current_player = self._rules.current_player(node.state)

        scores: list[float] = []

        for child in node.children:
            mean_value = child.value / child.visits

            # value は root_player 視点で記録している。
            # 相手の手番では root_player にとって小さい値を
            # 相手が選ぶと考える。
            if current_player is not root_player:
                mean_value = -mean_value

            exploration = self.exploration_weight * math.sqrt(
                math.log(node.visits) / child.visits
            )

            scores.append(mean_value + exploration)

        return node.children[argmax(scores)]

    def _expand(self, node: _MCTSNode) -> _MCTSNode:
        action = node.untried_actions.pop()

        next_state = self._rules.apply_action(node.state, action)

        child = self._make_node(
            state=next_state,
            parent=node,
            action=action,
        )
        node.children.append(child)

        return child

    def _playout(
        self,
        state: TicTacToeState,
        root_player: Player,
    ) -> float:
        while not self._rules.is_terminal(state):
            legal_actions = self._rules.legal_actions(state)
            action = self._rg.choice(legal_actions)
            state = self._rules.apply_action(state, action)

        result = self._rules.result(state)

        if result is not None:
            winner = result.winner

            if winner is root_player:
                return 1.0
            elif winner is root_player.opponent:
                return -1.0
            else:
                return 0.0

        raise RuntimeError("Game ended without a result.")

    def _backpropagate(
        self,
        node: _MCTSNode,
        score: float,
    ) -> None:
        while node is not None:
            node.visits += 1
            node.value += score
            node = node.parent
