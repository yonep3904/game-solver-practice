from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from game_solver.core import Player
from game_solver.games.connect_four import (
    ConnectFourAction,
    ConnectFourAgent,
    ConnectFourState,
)

from .alpha_zero.engine import ConnectFourEngine, ConnectFourPosition


@dataclass(slots=True)
class _Node:
    position: ConnectFourPosition
    action: int | None = None
    visits: int = 0
    value_sum: float = 0.0
    children: list[_Node] = field(default_factory=list)
    unexpanded_actions: list[int] = field(default_factory=list)

    @property
    def value(self) -> float:
        """Mean result from the player-to-move's perspective."""
        return self.value_sum / self.visits if self.visits else 0.0


class ConnectFourMCTSAgent(ConnectFourAgent):
    """Classic UCT MCTS using random rollouts and no machine learning."""

    def __init__(
        self,
        *,
        simulations: int = 1_000,
        exploration: float = math.sqrt(2.0),
        seed: int | None = None,
    ) -> None:
        if simulations <= 0:
            raise ValueError("simulations must be positive")
        if exploration < 0:
            raise ValueError("exploration must be non-negative")
        self.simulations = simulations
        self.exploration = exploration
        self.random = random.Random(seed)
        self.engine = ConnectFourEngine()

    def select_action(self, state: ConnectFourState) -> ConnectFourAction:
        position = self.engine.from_state(state)
        legal = self.engine.legal_actions(position)
        if not legal:
            raise ValueError("No legal actions available.")
        if len(legal) == 1:
            return ConnectFourAction(legal[0])

        root = self._new_node(position)
        for _ in range(self.simulations):
            node = root
            path = [root]

            while not node.unexpanded_actions and node.children:
                node = self._select_child(node)
                path.append(node)

            if node.unexpanded_actions:
                action_index = self.random.randrange(len(node.unexpanded_actions))
                action = node.unexpanded_actions.pop(action_index)
                node = self._new_node(self.engine.play(node.position, action), action)
                path[-1].children.append(node)
                path.append(node)

            winner = self._rollout(node.position)
            for visited in path:
                visited.visits += 1
                if winner is not None:
                    visited.value_sum += (
                        1.0 if visited.position.current_player is winner else -1.0
                    )

        most_visits = max(child.visits for child in root.children)
        choices = [child for child in root.children if child.visits == most_visits]
        action = self.random.choice(choices).action
        assert action is not None
        return ConnectFourAction(action)

    def _new_node(
        self, position: ConnectFourPosition, action: int | None = None
    ) -> _Node:
        actions = list(self.engine.legal_actions(position))
        self.random.shuffle(actions)
        return _Node(position, action=action, unexpanded_actions=actions)

    def _select_child(self, parent: _Node) -> _Node:
        log_parent = math.log(parent.visits)

        def uct(child: _Node) -> float:
            # Child values belong to the opponent, hence the minus sign.
            exploitation = -child.value
            exploration = self.exploration * math.sqrt(log_parent / child.visits)
            return exploitation + exploration

        best_score = max(uct(child) for child in parent.children)
        choices = [child for child in parent.children if uct(child) == best_score]
        return self.random.choice(choices)

    def _rollout(self, position: ConnectFourPosition) -> Player | None:
        while self.engine.terminal_value(position) is None:
            action = self.random.choice(self.engine.legal_actions(position))
            position = self.engine.play(position, action)
        value = self.engine.terminal_value(position)
        return None if value == 0 else position.current_player.opponent()
