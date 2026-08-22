from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import Tensor, nn
from torch.utils.data import DataLoader, TensorDataset

from .engine import ConnectFourEngine, ConnectFourPosition
from .mcts import AlphaZeroMCTS
from .network import ConnectFourPolicyValueNetwork


@dataclass(frozen=True)
class TrainingConfig:
    iterations: int = 5
    self_play_games: int = 10
    simulations: int = 100
    epochs: int = 3
    batch_size: int = 64
    replay_capacity: int = 20_000
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    exploration: float = 1.5
    temperature: float = 1.0

    def __post_init__(self) -> None:
        positive = {
            "iterations": self.iterations,
            "self_play_games": self.self_play_games,
            "simulations": self.simulations,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "replay_capacity": self.replay_capacity,
            "learning_rate": self.learning_rate,
            "temperature": self.temperature,
        }
        for name, value in positive.items():
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        if self.weight_decay < 0 or self.exploration < 0:
            raise ValueError("weight_decay and exploration must be non-negative")


@dataclass(frozen=True)
class TrainingMetrics:
    iteration: int
    examples: int
    policy_loss: float
    value_loss: float


@dataclass(frozen=True)
class _Example:
    state: Tensor
    policy: Tensor
    value: float


class ConnectFourAlphaZeroTrainer:
    """Educational self-play, replay-buffer, and optimization loop."""

    def __init__(
        self,
        network: ConnectFourPolicyValueNetwork | None = None,
        *,
        config: TrainingConfig | None = None,
        device: str | torch.device | None = None,
        seed: int | None = None,
    ) -> None:
        self.config = config or TrainingConfig()
        self.device = torch.device(device or "cpu")
        self.network = (network or ConnectFourPolicyValueNetwork()).to(self.device)
        self.optimizer = torch.optim.AdamW(
            self.network.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
        )
        self.engine = ConnectFourEngine()
        self.replay: deque[_Example] = deque(maxlen=self.config.replay_capacity)
        self.random = random.Random(seed)
        self.seed = seed
        self.completed_iterations = 0

    def train(self) -> list[TrainingMetrics]:
        history: list[TrainingMetrics] = []
        for _ in range(self.config.iterations):
            for _ in range(self.config.self_play_games):
                self.replay.extend(self.self_play_game())
            policy_loss, value_loss = self._optimize()
            self.completed_iterations += 1
            history.append(
                TrainingMetrics(
                    self.completed_iterations,
                    len(self.replay),
                    policy_loss,
                    value_loss,
                )
            )
        return history

    def self_play_game(self) -> list[_Example]:
        self.network.eval()
        mcts = AlphaZeroMCTS(
            self.network,
            self.engine,
            simulations=self.config.simulations,
            exploration=self.config.exploration,
            device=self.device,
            seed=self.random.randrange(2**32),
        )
        position = self.engine.initial_position()
        trajectory: list[tuple[ConnectFourPosition, Tensor]] = []
        while self.engine.terminal_value(position) is None:
            visits = mcts.search(position)
            policy = torch.zeros(7)
            exponent = 1.0 / self.config.temperature
            total = sum(count**exponent for count in visits.values())
            for column, count in visits.items():
                policy[column] = count**exponent / total
            trajectory.append((position, policy))
            column = self.random.choices(range(7), weights=policy.tolist(), k=1)[0]
            position = self.engine.play(position, column)

        terminal_value = self.engine.terminal_value(position)
        assert terminal_value is not None
        winner = None if terminal_value == 0 else position.current_player.opponent()
        examples: list[_Example] = []
        for old_position, policy in trajectory:
            value = (
                0.0
                if winner is None
                else (1.0 if old_position.current_player is winner else -1.0)
            )
            state = self.engine.encode(old_position, device=torch.device("cpu"))
            examples.append(_Example(state, policy, value))
            examples.append(_Example(state.flip(2), policy.flip(0), value))
        return examples

    def _optimize(self) -> tuple[float, float]:
        states = torch.stack([example.state for example in self.replay])
        policies = torch.stack([example.policy for example in self.replay])
        values = torch.tensor([example.value for example in self.replay])
        loader = DataLoader(
            TensorDataset(states, policies, values),
            batch_size=self.config.batch_size,
            shuffle=True,
        )
        self.network.train()
        policy_total = value_total = 0.0
        batches = 0
        for _ in range(self.config.epochs):
            for state_batch, policy_batch, value_batch in loader:
                logits, predictions = self.network(state_batch.to(self.device))
                policy_batch = policy_batch.to(self.device)
                value_batch = value_batch.to(self.device)
                policy_loss = (
                    -(policy_batch * logits.log_softmax(dim=1)).sum(dim=1).mean()
                )
                value_loss = nn.functional.mse_loss(predictions, value_batch)
                self.optimizer.zero_grad()
                (policy_loss + value_loss).backward()
                self.optimizer.step()
                policy_total += policy_loss.item()
                value_total += value_loss.item()
                batches += 1
        self.network.eval()
        return policy_total / batches, value_total / batches

    def save_checkpoint(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_state_dict": self.network.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "channels": self.network.channels,
                "residual_blocks": self.network.residual_blocks,
                "completed_iterations": self.completed_iterations,
            },
            destination,
        )

    def load_checkpoint(self, path: str | Path) -> None:
        checkpoint = torch.load(path, map_location=self.device, weights_only=True)
        architecture = (checkpoint["channels"], checkpoint["residual_blocks"])
        if architecture != (self.network.channels, self.network.residual_blocks):
            raise ValueError("checkpoint network architecture does not match")
        self.network.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.completed_iterations = int(checkpoint.get("completed_iterations", 0))
