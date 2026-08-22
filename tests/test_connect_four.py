from __future__ import annotations

import sys

sys.path.append("../src")

import unittest

from game_solver.core import Player
from game_solver.games.connect_four import (
    ConnectFourAction,
    ConnectFourGameRules,
    ConnectFourState,
)
from game_solver.games.connect_four.state import BOARD_WIDTH


class ConnectFourGameRulesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rules = ConnectFourGameRules()

    def play_columns(self, columns: list[int]) -> ConnectFourState:
        state = self.rules.initial_state()
        for column in columns:
            state = self.rules.apply_action(state, ConnectFourAction(column))
        return state

    def test_piece_falls_to_lowest_empty_cell(self) -> None:
        state = self.play_columns([2, 2])
        self.assertEqual(state.board[5 * BOARD_WIDTH + 2], Player.FIRST)
        self.assertEqual(state.board[4 * BOARD_WIDTH + 2], Player.SECOND)

    def test_horizontal_win(self) -> None:
        state = self.play_columns([0, 0, 1, 1, 2, 2, 3])
        self.assertTrue(self.rules.is_terminal(state))
        self.assertEqual(self.rules.winner(state), Player.FIRST)

    def test_vertical_win(self) -> None:
        state = self.play_columns([0, 1, 0, 1, 0, 1, 0])
        self.assertEqual(self.rules.winner(state), Player.FIRST)

    def test_both_diagonal_directions(self) -> None:
        ascending = self.play_columns([0, 1, 1, 2, 4, 2, 2, 3, 4, 3, 5, 3, 3])
        descending = self.play_columns([3, 2, 2, 1, 6, 1, 1, 0, 6, 0, 5, 0, 0])
        self.assertEqual(self.rules.winner(ascending), Player.FIRST)
        self.assertEqual(self.rules.winner(descending), Player.FIRST)

    def test_full_column_is_not_legal(self) -> None:
        state = self.play_columns([0, 0, 0, 0, 0, 0])
        action = ConnectFourAction(0)
        self.assertFalse(self.rules.is_legal_action(state, action))
        self.assertNotIn(action, self.rules.legal_actions(state))
        with self.assertRaises(ValueError):
            self.rules.apply_action(state, action)

    def test_string_representation_has_six_rows(self) -> None:
        state = self.play_columns([0])
        rows = str(state).splitlines()
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[-1], "X......")


if __name__ == "__main__":
    unittest.main()
