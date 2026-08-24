from __future__ import annotations

import math
import random

from game_solver.games.tic_tac_toe import (
    TicTacToeAction,
    TicTacToeAgent,
    TicTacToeState,
)

from .engine import TicTacToeEngine, TicTacToeEngineAction, TicTacToeEngineState


class MCTSNode:
    def __init__(
        self,
        state: TicTacToeEngineState,
        parent: MCTSNode | None = None,
        action: TicTacToeEngineAction | None = None,
    ):
        self.state = state
        self.parent = parent
        self.action = action

        self.children: list[MCTSNode] = []
        self.untried_actions: list[TicTacToeEngineAction] = []

        # Sum of outcomes from state.current_player's perspective.
        self.value_sum = 0.0
        self.visit_count = 0


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

        self._engine = TicTacToeEngine()
        self._rg = random.Random(seed)

    def select_action(self, state: TicTacToeState) -> TicTacToeAction:
        engine_state = self._engine.from_state(state)
        actions = self._engine.legal_actions(engine_state)

        if not actions:
            raise ValueError("No legal actions available.")

        root = self._make_node(engine_state)

        for _ in range(self.simulations):
            node = root

            # 1. Selection: 探索価値の高い葉ノードまで降りていく
            node = self._select(node)

            # 2. Expansion: 未探索の子ノードがあれば1つ展開する
            if node.untried_actions:
                node = self._expand(node)

            # 3. Simulation: 終局までランダムに進めて結果を得る
            score = self._simulate(node.state)

            # 4. Backpropagation: 結果を親ノードに逆伝播させる
            self._backpropagate(node, score)

        # 最も多く探索された子を選ぶ
        choice = max(
            root.children,
            key=lambda child: child.visit_count,
        ).action

        if choice is None:
            raise RuntimeError("No action selected.")

        return self._engine.to_action(choice)

    def _make_node(
        self,
        state: TicTacToeEngineState,
        parent: MCTSNode | None = None,
        action: TicTacToeEngineAction | None = None,
    ) -> MCTSNode:
        node = MCTSNode(
            state=state,
            parent=parent,
            action=action,
        )
        node.untried_actions = list(self._engine.legal_actions(state))
        self._rg.shuffle(node.untried_actions)

        return node

    @staticmethod
    def _uct(
        value_sum: float,
        visits: int,
        parent_visits: int,
        *,
        exploration_weight: float,
    ) -> float:
        if visits == 0:
            return float("inf")

        exploitation = -value_sum / visits
        exploration = exploration_weight * math.sqrt(math.log(parent_visits) / visits)

        return exploitation + exploration

    def _select(self, node: MCTSNode) -> MCTSNode:
        current = node

        while not self._engine.is_terminal(current.state):
            if current.untried_actions:
                break

            current = max(
                current.children,
                key=lambda child: self._uct(
                    child.value_sum,
                    child.visit_count,
                    current.visit_count,
                    exploration_weight=self.exploration_weight,
                ),
            )

        return current

    def _expand(self, node: MCTSNode) -> MCTSNode:
        action = node.untried_actions.pop()

        next_state = self._engine.apply_action(node.state, action)

        child = self._make_node(next_state, node, action)
        node.children.append(child)

        return child

    def _simulate(
        self,
        state: TicTacToeEngineState,
    ) -> float:
        current = state

        # Playout
        while not self._engine.is_terminal(current):
            legal_actions = self._engine.legal_actions(current)
            action = self._rg.choice(legal_actions)
            current = self._engine.apply_action(current, action)

        player = self._engine.current_player(state)
        result = self._engine.result(current)

        if result is not None:
            winner = result.winner

            if winner is player:
                return 1.0
            elif winner is player.opponent:
                return -1.0
            else:
                return 0.0

        raise RuntimeError("Game ended without a result.")

    def _backpropagate(
        self,
        node: MCTSNode,
        score: float,
    ) -> None:
        current = node

        while current is not None:
            current.visit_count += 1
            current.value_sum += score

            score = -score
            current = current.parent
