from __future__ import annotations

import random
import tempfile
import unittest
from pathlib import Path

import torch

from game_solver.agents.connect_four import (
    ConnectFourMCTSAgent,
    ConnectFourRandomAgent,
)
from game_solver.agents.connect_four.alpha_zero import (
    ConnectFourAlphaZeroAgent,
    ConnectFourAlphaZeroTrainer,
    ConnectFourEngine,
    ConnectFourPolicyValueNetwork,
    TrainingConfig,
)
from game_solver.core import Arena, ArenaCompetitor
from game_solver.games.connect_four import ConnectFourAction, ConnectFourGameRules


class ConnectFourEngineTest(unittest.TestCase):
    def test_engine_agrees_with_official_rules_on_random_games(self) -> None:
        random_source = random.Random(0)
        rules = ConnectFourGameRules()

        for _ in range(30):
            state = rules.initial_state()
            position = ConnectFourEngine.initial_position()
            while not rules.is_terminal(state):
                expected = tuple(action.column for action in rules.legal_actions(state))
                self.assertEqual(ConnectFourEngine.legal_actions(position), expected)
                column = random_source.choice(expected)
                state = rules.apply_action(state, ConnectFourAction(column))
                position = ConnectFourEngine.play(position, column)

            result = rules.result(state)
            self.assertIsNotNone(result)
            winner = result.winner()  # type: ignore[union-attr]
            expected_value = 0.0 if winner is None else -1.0
            self.assertEqual(ConnectFourEngine.terminal_value(position), expected_value)

    def test_state_conversion_preserves_position(self) -> None:
        rules = ConnectFourGameRules()
        state = rules.initial_state()
        position = ConnectFourEngine.initial_position()
        for column in (3, 2, 3, 4, 2):
            state = rules.apply_action(state, ConnectFourAction(column))
            position = ConnectFourEngine.play(position, column)
        self.assertEqual(ConnectFourEngine.from_state(state), position)


class ConnectFourAlphaZeroAgentTest(unittest.TestCase):
    def test_network_output_shapes(self) -> None:
        network = ConnectFourPolicyValueNetwork(channels=8, residual_blocks=1)
        policy, value = network(torch.zeros((2, 3, 6, 7)))
        self.assertEqual(policy.shape, (2, 7))
        self.assertEqual(value.shape, (2,))

    def test_agent_returns_legal_action(self) -> None:
        rules = ConnectFourGameRules()
        state = rules.initial_state()
        agent = ConnectFourAlphaZeroAgent(
            ConnectFourPolicyValueNetwork(channels=8, residual_blocks=0),
            simulations=4,
            seed=0,
        )
        self.assertIn(agent.select_action(state), rules.legal_actions(state))

    def test_parameter_round_trip(self) -> None:
        network = ConnectFourPolicyValueNetwork(channels=8, residual_blocks=0)
        agent = ConnectFourAlphaZeroAgent(network, simulations=1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "parameters.pt"
            agent.save_parameters(path)
            restored = ConnectFourAlphaZeroAgent.from_parameters(path, simulations=1)
        for expected, actual in zip(
            agent.network.parameters(), restored.network.parameters(), strict=True
        ):
            self.assertTrue(torch.equal(expected, actual))

    def test_random_agent_returns_legal_action(self) -> None:
        rules = ConnectFourGameRules()
        state = rules.initial_state()
        self.assertIn(
            ConnectFourRandomAgent(seed=0).select_action(state),
            rules.legal_actions(state),
        )

    def test_plain_mcts_returns_legal_action(self) -> None:
        rules = ConnectFourGameRules()
        state = rules.initial_state()
        agent = ConnectFourMCTSAgent(simulations=10, seed=0)
        self.assertIn(agent.select_action(state), rules.legal_actions(state))


class ConnectFourAlphaZeroTrainerTest(unittest.TestCase):
    def test_training_and_checkpoint(self) -> None:
        config = TrainingConfig(
            iterations=1,
            self_play_games=1,
            simulations=1,
            epochs=1,
            batch_size=128,
        )
        network = ConnectFourPolicyValueNetwork(channels=4, residual_blocks=0)
        trainer = ConnectFourAlphaZeroTrainer(network, config=config, seed=0)
        history = trainer.train()
        self.assertEqual(len(history), 1)
        self.assertGreater(history[0].examples, 0)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            trainer.save_checkpoint(path)
            restored = ConnectFourAlphaZeroTrainer(
                ConnectFourPolicyValueNetwork(channels=4, residual_blocks=0),
                config=config,
            )
            restored.load_checkpoint(path)
            self.assertEqual(restored.completed_iterations, 1)


class ArenaTest(unittest.TestCase):
    def test_play_and_ranking(self) -> None:
        arena = Arena(ConnectFourGameRules())
        first = ArenaCompetitor("random-a", lambda: ConnectFourRandomAgent(1))
        second = ArenaCompetitor("random-b", lambda: ConnectFourRandomAgent(2))
        third = ArenaCompetitor("random-c", lambda: ConnectFourRandomAgent(3))

        evaluation = arena.play(first, second, games=2)
        self.assertEqual(evaluation.games, 2)
        self.assertEqual(evaluation.agent_class, "ConnectFourRandomAgent")
        self.assertEqual(len(evaluation.matches), 2)
        self.assertEqual(evaluation.matches[0].first_agent, "random-a")
        self.assertEqual(evaluation.matches[1].first_agent, "random-b")

        ranking = arena.rank([first, second, third], games_per_pair=2)
        self.assertEqual(len(ranking.standings), 3)
        self.assertEqual(len(ranking.pairings), 3)
        self.assertEqual(
            {standing.agent_name for standing in ranking.standings},
            {"random-a", "random-b", "random-c"},
        )


if __name__ == "__main__":
    unittest.main()
