from __future__ import annotations

import sys

sys.path.append("../src")

print(sys.path)

import unittest

from game_solver.agents.tic_tac_toe import (
    TicTacToeAlphaBetaAgent,
    TicTacToeMinimaxAgent,
    TicTacToeMonteCarloAgent,
    TicTacToePrimitiveMCTSAgent,
)
from game_solver.core import Player
from game_solver.games.tic_tac_toe import TicTacToeState


class TicTacToeSearchAgentsTest(unittest.TestCase):
    def test_minimax_and_alpha_beta_take_immediate_win(self) -> None:
        state = TicTacToeState(
            board=(
                Player.FIRST,
                Player.FIRST,
                None,
                Player.SECOND,
                Player.SECOND,
                None,
                None,
                None,
                None,
            ),
            current_player=Player.FIRST,
        )
        for agent in (TicTacToeMinimaxAgent(), TicTacToeAlphaBetaAgent()):
            with self.subTest(agent=type(agent).__name__):
                self.assertEqual(agent.select_action(state).position, 2)

    def test_minimax_and_alpha_beta_block_forced_loss(self) -> None:
        state = TicTacToeState(
            board=(
                Player.SECOND,
                Player.SECOND,
                None,
                Player.FIRST,
                None,
                None,
                Player.FIRST,
                None,
                None,
            ),
            current_player=Player.FIRST,
        )
        for agent in (TicTacToeMinimaxAgent(), TicTacToeAlphaBetaAgent()):
            with self.subTest(agent=type(agent).__name__):
                self.assertEqual(agent.select_action(state).position, 2)

    def test_monte_carlo_agents_return_legal_action(self) -> None:
        state = TicTacToeState(
            board=(
                Player.FIRST,
                None,
                Player.SECOND,
                None,
                Player.FIRST,
                None,
                None,
                None,
                Player.SECOND,
            ),
            current_player=Player.FIRST,
        )
        agents = (
            TicTacToePrimitiveMCTSAgent(simulations_per_action=10, seed=1),
            TicTacToeMonteCarloAgent(simulations=30, seed=1),
        )
        for agent in agents:
            with self.subTest(agent=type(agent).__name__):
                self.assertIsNone(state.board[agent.select_action(state).position])

    def test_agents_reject_terminal_state(self) -> None:
        state = TicTacToeState(
            board=(
                Player.FIRST,
                Player.FIRST,
                Player.FIRST,
                Player.SECOND,
                Player.SECOND,
                None,
                None,
                None,
                None,
            ),
            current_player=Player.SECOND,
        )
        agents = (
            TicTacToeMinimaxAgent(),
            TicTacToeAlphaBetaAgent(),
            TicTacToePrimitiveMCTSAgent(),
            TicTacToeMonteCarloAgent(),
        )

        for agent in agents:
            with (
                self.subTest(agent=type(agent).__name__),
                self.assertRaises(ValueError),
            ):
                agent.select_action(state)

    def test_positive_simulation_counts_are_required(self) -> None:
        with self.assertRaises(ValueError):
            TicTacToePrimitiveMCTSAgent(simulations_per_action=0)
        with self.assertRaises(ValueError):
            TicTacToeMonteCarloAgent(simulations=0)


if __name__ == "__main__":
    unittest.main()
