"""A small, educational AlphaZero implementation for Connect Four."""

from .agent import ConnectFourAlphaZeroAgent
from .engine import ConnectFourEngine, ConnectFourPosition
from .network import ConnectFourPolicyValueNetwork
from .training import (
    ConnectFourAlphaZeroTrainer,
    TrainingConfig,
    TrainingMetrics,
)

__all__ = [
    "ConnectFourAlphaZeroAgent",
    "ConnectFourAlphaZeroTrainer",
    "ConnectFourEngine",
    "ConnectFourPolicyValueNetwork",
    "ConnectFourPosition",
    "TrainingConfig",
    "TrainingMetrics",
]
