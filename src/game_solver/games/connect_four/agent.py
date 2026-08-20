from __future__ import annotations

from game_solver.core import Agent

from .action import ConnectFourAction
from .state import ConnectFourState


class ConnectFourAgent(Agent[ConnectFourState, ConnectFourAction]): ...
