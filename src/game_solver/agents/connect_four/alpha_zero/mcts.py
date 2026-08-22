from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import torch
from torch import nn

from .engine import ConnectFourEngine, ConnectFourPosition


@dataclass(slots=True)
class _Node:
    prior: float
    visit_count: int = 0
    value_sum: float = 0.0
    children: dict[int, _Node] = field(default_factory=dict)

    @property
    def value(self) -> float:
        return self.value_sum / self.visit_count if self.visit_count else 0.0


class AlphaZeroMCTS:
    """PUCT tree search. Node values use the player-to-move perspective."""

    def __init__(
        self,
        network: nn.Module,
        engine: ConnectFourEngine,
        *,
        simulations: int,
        exploration: float,
        device: torch.device,
        seed: int | None = None,
    ) -> None:
        self.network = network
        self.engine = engine
        self.simulations = simulations
        self.exploration = exploration
        self.device = device
        self.random = random.Random(seed)

    def search(self, position: ConnectFourPosition) -> dict[int, int]:
        root = _Node(1.0)
        self._expand(root, position)
        for _ in range(self.simulations):
            node, current = root, position
            path = [root]
            while node.children:
                action, node = self._select_child(node)
                current = self.engine.play(current, action)
                path.append(node)
                if self.engine.terminal_value(current) is not None:
                    break

            value = self.engine.terminal_value(current)
            if value is None:
                value = self._expand(node, current)
            for visited in reversed(path):
                visited.visit_count += 1
                visited.value_sum += value
                value = -value
        return {action: child.visit_count for action, child in root.children.items()}

    def _expand(self, node: _Node, position: ConnectFourPosition) -> float:
        legal = self.engine.legal_actions(position)
        if not legal:
            return self.engine.terminal_value(position) or 0.0
        encoded = self.engine.encode(position, device=self.device).unsqueeze(0)
        with torch.inference_mode():
            logits, value = self.network(encoded)
            masked = torch.full_like(logits[0], -torch.inf)
            masked[list(legal)] = logits[0, list(legal)]
            probabilities = torch.softmax(masked, dim=0).cpu().tolist()
        node.children = {
            action: _Node(float(probabilities[action])) for action in legal
        }
        return float(value.item())

    def _select_child(self, parent: _Node) -> tuple[int, _Node]:
        scale = math.sqrt(max(1, parent.visit_count))

        def score(item: tuple[int, _Node]) -> float:
            _, child = item
            # A child value belongs to the opponent, hence the minus sign.
            return -child.value + self.exploration * child.prior * scale / (
                child.visit_count + 1
            )

        best = max(score(item) for item in parent.children.items())
        choices = [item for item in parent.children.items() if score(item) == best]
        return self.random.choice(choices)
