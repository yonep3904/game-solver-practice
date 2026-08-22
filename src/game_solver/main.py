from __future__ import annotations

import sys

sys.path.append("..")

import argparse
from pathlib import Path

from game_solver.agents.connect_four.alpha_zero import (
    ConnectFourAlphaZeroAgent,
    ConnectFourAlphaZeroTrainer,
    TrainingConfig,
)
from game_solver.agents.connect_four.mcts import ConnectFourMCTSAgent
from game_solver.core import Arena, Competitor
from game_solver.games.connect_four import ConnectFourGameRules


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a small Connect Four AlphaZero")
    parser.add_argument("--iterations", type=int, default=2)
    parser.add_argument("--self-play-games", type=int, default=4)
    parser.add_argument("--simulations", type=int, default=50)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--evaluation-games", type=int, default=10)
    parser.add_argument("--mcts-simulations", type=int, default=1_000)
    parser.add_argument(
        "--checkpoint", type=Path, default=Path("connect_four_alpha_zero.pt")
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = TrainingConfig(
        iterations=args.iterations,
        self_play_games=args.self_play_games,
        simulations=args.simulations,
        epochs=args.epochs,
    )
    trainer = ConnectFourAlphaZeroTrainer(
        config=config, device=args.device, seed=args.seed
    )
    if args.resume:
        trainer.load_checkpoint(args.checkpoint)

    for metrics in trainer.train():
        print(
            f"iteration={metrics.iteration} examples={metrics.examples} "
            f"policy_loss={metrics.policy_loss:.4f} "
            f"value_loss={metrics.value_loss:.4f}"
        )
    trainer.save_checkpoint(args.checkpoint)
    arena = Arena(ConnectFourGameRules())
    result = arena.play(
        Competitor(
            "AlphaZero",
            lambda: ConnectFourAlphaZeroAgent(
                trainer.network,
                simulations=args.simulations,
                device=args.device,
            ),
        ),
        Competitor(
            "MCTS",
            lambda: ConnectFourMCTSAgent(
                simulations=args.mcts_simulations,
            ),
        ),
        games=args.evaluation_games,
    )
    print(
        f"checkpoint={args.checkpoint} evaluation: wins={result.wins} "
        f"draws={result.draws} losses={result.losses} "
        f"win_rate={result.win_rate:.1%} score={result.score_rate:.1%}"
    )

    print(result)


if __name__ == "__main__":
    main()
