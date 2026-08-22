from __future__ import annotations

import random
from pathlib import Path

import torch

from game_solver.games.connect_four import (
    ConnectFourAction,
    ConnectFourAgent,
    ConnectFourState,
)

from .engine import ConnectFourEngine
from .mcts import AlphaZeroMCTS
from .network import ConnectFourPolicyValueNetwork


class ConnectFourAlphaZeroAgent(ConnectFourAgent):
    """Choose moves with a policy/value network guided Monte Carlo tree search.

    An untrained network is created by default. Useful play requires passing a
    trained network (or loading its ``state_dict``) but even an untrained model
    still produces legal moves and exercises the complete AlphaZero search path.
    """

    def __init__(
        self,
        network: ConnectFourPolicyValueNetwork | None = None,
        *,
        simulations: int = 200,
        exploration: float = 1.5,
        temperature: float = 0.0,
        device: str | torch.device | None = None,
        seed: int | None = None,
    ) -> None:
        if simulations <= 0:
            raise ValueError("simulations must be positive")
        if exploration < 0:
            raise ValueError("exploration must be non-negative")
        if temperature < 0:
            raise ValueError("temperature must be non-negative")
        self.device = torch.device(device or "cpu")
        self.network = (network or ConnectFourPolicyValueNetwork()).to(self.device)
        self.network.eval()
        self.engine = ConnectFourEngine()
        self.temperature = temperature
        self.random = random.Random(seed)
        self.mcts = AlphaZeroMCTS(
            self.network,
            self.engine,
            simulations=simulations,
            exploration=exploration,
            device=self.device,
            seed=seed,
        )

    def select_action(self, state: ConnectFourState) -> ConnectFourAction:
        position = self.engine.from_state(state)
        legal = self.engine.legal_actions(position)
        if not legal:
            raise ValueError("No legal actions available.")
        if len(legal) == 1:
            return ConnectFourAction(legal[0])

        visits = self.mcts.search(position)
        if self.temperature == 0:
            maximum = max(visits.values())
            columns = [column for column, count in visits.items() if count == maximum]
            return ConnectFourAction(self.random.choice(columns))

        weights = [visits[column] ** (1.0 / self.temperature) for column in legal]
        return ConnectFourAction(self.random.choices(legal, weights=weights, k=1)[0])

    def save_parameters(self, path: str | Path) -> None:
        """Save parameters and network architecture metadata."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_state_dict": self.network.state_dict(),
                "channels": self.network.channels,
                "residual_blocks": self.network.residual_blocks,
            },
            destination,
        )

    @classmethod
    def from_parameters(
        cls,
        path: str | Path,
        *,
        device: str | torch.device | None = None,
        **agent_options: object,
    ) -> ConnectFourAlphaZeroAgent:
        target_device = torch.device(device or "cpu")
        checkpoint = torch.load(path, map_location=target_device, weights_only=True)
        network = ConnectFourPolicyValueNetwork(
            channels=int(checkpoint["channels"]),
            residual_blocks=int(checkpoint["residual_blocks"]),
        )
        network.load_state_dict(checkpoint["model_state_dict"])
        return cls(network, device=target_device, **agent_options)
