from __future__ import annotations

from game_solver.core import Agent

from .action import TicTacToeAction
from .state import TicTacToeState


class TicTacToeAgent(Agent[TicTacToeState, TicTacToeAction]): ...
