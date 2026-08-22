from __future__ import annotations

from torch import Tensor, nn

from game_solver.games.connect_four.constants import BOARD_HEIGHT, BOARD_WIDTH


class _ResidualBlock(nn.Module):
    def __init__(self, channels: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Conv2d(channels, channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
            nn.Conv2d(channels, channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(channels),
        )
        self.activation = nn.ReLU()

    def forward(self, inputs: Tensor) -> Tensor:
        return self.activation(inputs + self.layers(inputs))


class ConnectFourPolicyValueNetwork(nn.Module):
    """Small residual policy/value network suitable for learning experiments."""

    def __init__(self, channels: int = 64, residual_blocks: int = 3) -> None:
        super().__init__()
        if channels <= 0 or residual_blocks < 0:
            raise ValueError(
                "channels must be positive and residual_blocks non-negative"
            )

        self.channels = channels
        self.residual_blocks = residual_blocks

        self.trunk = nn.Sequential(
            nn.Conv2d(3, channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
            *(_ResidualBlock(channels) for _ in range(residual_blocks)),
        )
        self.policy_head = nn.Sequential(
            nn.Conv2d(channels, 2, 1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(2 * BOARD_HEIGHT * BOARD_WIDTH, BOARD_WIDTH),
        )
        self.value_head = nn.Sequential(
            nn.Conv2d(channels, 1, 1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(BOARD_HEIGHT * BOARD_WIDTH, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Tanh(),
        )

    def forward(self, inputs: Tensor) -> tuple[Tensor, Tensor]:
        features = self.trunk(inputs)
        return self.policy_head(features), self.value_head(features).squeeze(-1)
