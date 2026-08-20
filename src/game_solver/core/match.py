from __future__ import annotations

from dataclasses import dataclass

from .agent import Agent
from .game import GameRules
from .types import GameResult, Player

DEFAULT_TURN_LIMIT = 10_000_000  # 無限ループ防止のための上限値

# TODO: 試合のログを記録する機能を追加する（必要になれば）


@dataclass(frozen=True)
class MatchResult:
    winner: GameResult
    count: int


class Match[StateT, ActionT]:
    def __init__(
        self,
        game_rules: GameRules[StateT, ActionT],
        first_agent: Agent[StateT, ActionT],
        second_agent: Agent[StateT, ActionT],
        turn_limit: int = DEFAULT_TURN_LIMIT,
    ) -> None:
        if turn_limit <= 0:
            raise ValueError("turn_limit must be positive")

        self.game_rules = game_rules
        self.first_agent = first_agent
        self.second_agent = second_agent
        self.turn_limit = turn_limit

        self.state: StateT
        self.count: int

        self.reset()

    def reset(self) -> StateT:
        """ゲームを初期状態にリセットする。"""
        self.state = self.game_rules.initial_state()
        self.count = 0

        return self.state

    def play_step(self) -> StateT:
        """ゲームを1ターン進める。"""
        if self.game_rules.is_terminal(self.state):
            raise RuntimeError("Match has already finished")

        if self.count >= self.turn_limit:
            raise RuntimeError(f"Match did not finish within {self.turn_limit} turns")

        current_player = self.game_rules.current_player(self.state)
        agent = (
            self.first_agent if current_player == Player.FIRST else self.second_agent
        )
        action = agent.select_action(self.state)

        if not self.game_rules.is_legal_action(self.state, action):
            raise ValueError(f"Illegal action: {action}")

        self.state = self.game_rules.apply_action(self.state, action)
        self.count += 1

        return self.state

    def is_terminal(self) -> bool:
        """ゲームが終了しているかどうかを返す。"""
        return self.game_rules.is_terminal(self.state)

    def current_player(self) -> Player:
        """現在の状態での手番のプレイヤーを返す。"""
        if self.is_terminal():
            raise RuntimeError("Match has already finished")

        return self.game_rules.current_player(self.state)

    def result(self) -> GameResult | None:
        """勝者または引き分けを返す。ゲームが終了していない場合は None を返す。"""
        return self.game_rules.result(self.state)

    def play(self) -> MatchResult:
        """ゲームを開始し、終了するまで進める。"""
        while not self.game_rules.is_terminal(self.state):
            self.play_step()

        result = self.game_rules.result(self.state)

        if result is None:
            raise RuntimeError("Match finished but result is None")

        return MatchResult(winner=result, count=self.count)
