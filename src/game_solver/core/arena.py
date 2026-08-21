from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import combinations
from typing import Literal

from .agent import Agent
from .game import GameRules
from .match import DEFAULT_TURN_LIMIT, Match, MatchResult
from .types import GameResult


@dataclass(frozen=True)
class Competitor[StateT, ActionT]:
    name: str
    factory: Callable[[], Agent[StateT, ActionT]]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("competitor name must not be empty")


@dataclass(frozen=True)
class ArenaMatchResult:
    match_number: int
    first_competitor_name: str
    second_competitor_name: str
    result: MatchResult


@dataclass(frozen=True)
class ArenaSeriesResult:
    competitor1_name: str
    competitor2_name: str
    matches: tuple[ArenaMatchResult, ...]


@dataclass(frozen=True)
class ArenaRoundRobinResult:
    series: tuple[ArenaSeriesResult, ...]
    ranking: tuple[tuple[str, int], ...]  # (competitor_name, score)


@dataclass(frozen=True)
class CompetitorEvaluation:
    competitor_name: str
    opponent_name: str

    matches: tuple[ArenaMatchResult, ...]

    first_player_index: tuple[int, ...]
    second_player_index: tuple[int, ...]

    @property
    def match_count(self) -> tuple[int, int, int]:
        first = len(self.first_player_index)
        second = len(self.second_player_index)
        return (first + second, first, second)

    @property
    def win_count(self) -> tuple[int, int, int]:
        first = sum(
            self.matches[i].result.result == GameResult.FIRST
            for i in self.first_player_index
        )
        second = sum(
            self.matches[i].result.result == GameResult.SECOND
            for i in self.second_player_index
        )
        return (first + second, first, second)

    @property
    def draw_count(self) -> tuple[int, int, int]:
        first = sum(
            self.matches[i].result.result == GameResult.DRAW
            for i in self.first_player_index
        )
        second = sum(
            self.matches[i].result.result == GameResult.DRAW
            for i in self.second_player_index
        )
        return (first + second, first, second)

    @property
    def loss_count(self) -> tuple[int, int, int]:
        first = sum(
            self.matches[i].result.result == GameResult.SECOND
            for i in self.first_player_index
        )
        second = sum(
            self.matches[i].result.result == GameResult.FIRST
            for i in self.second_player_index
        )
        return (first + second, first, second)

    @property
    def win_rate(self) -> tuple[float, float, float]:
        total, first, second = self.win_count
        matches = self.match_count
        return (
            total / matches[0] if matches[0] else 0.0,
            first / matches[1] if matches[1] else 0.0,
            second / matches[2] if matches[2] else 0.0,
        )

    @property
    def draw_rate(self) -> tuple[float, float, float]:
        total, first, second = self.draw_count
        matches = self.match_count
        return (
            total / matches[0] if matches[0] else 0.0,
            first / matches[1] if matches[1] else 0.0,
            second / matches[2] if matches[2] else 0.0,
        )

    @property
    def loss_rate(self) -> tuple[float, float, float]:
        total, first, second = self.loss_count
        matches = self.match_count
        return (
            total / matches[0] if matches[0] else 0.0,
            first / matches[1] if matches[1] else 0.0,
            second / matches[2] if matches[2] else 0.0,
        )


class Arena[StateT, ActionT]:
    def __init__(
        self,
        game_rules: GameRules[StateT, ActionT],
        turn_limit: int = DEFAULT_TURN_LIMIT,
    ) -> None:

        self.game_rules = game_rules
        self.turn_limit = turn_limit

    def play_match(
        self,
        first_competitor: Competitor[StateT, ActionT],
        second_competitor: Competitor[StateT, ActionT],
        match_number: int,
        save_log: bool = True,
    ) -> ArenaMatchResult:
        """1試合を実行する。"""

        match = Match(
            self.game_rules,
            first_competitor.factory(),
            second_competitor.factory(),
            turn_limit=self.turn_limit,
            save_log=save_log,
        )

        result = match.play()

        return ArenaMatchResult(
            match_number=match_number,
            first_competitor_name=first_competitor.name,
            second_competitor_name=second_competitor.name,
            result=result,
        )

    def play_series(
        self,
        competitor1: Competitor[StateT, ActionT],
        competitor2: Competitor[StateT, ActionT],
        num_matches: int,
        save_log: bool = True,
    ) -> ArenaSeriesResult:
        """複数試合を実行する。"""

        if num_matches <= 0:
            raise ValueError("num_matches must be positive")

        if competitor1.name == competitor2.name:
            raise ValueError("competitor1 and competitor2 must have different names")

        matches: list[ArenaMatchResult] = []

        for match_number in range(1, num_matches + 1):
            if match_number % 2 == 1:
                match_result = self.play_match(
                    competitor1, competitor2, match_number, save_log
                )
            else:
                match_result = self.play_match(
                    competitor2, competitor1, match_number, save_log
                )

            matches.append(match_result)

        return ArenaSeriesResult(
            competitor1_name=competitor1.name,
            competitor2_name=competitor2.name,
            matches=tuple(matches),
        )

    def play_round_robin(
        self,
        competitors: Sequence[Competitor[StateT, ActionT]],
        num_matches: int,
        save_log: bool = True,
        ranking_method: Literal["win_count", "point"] = "point",
    ) -> ArenaRoundRobinResult:
        """ラウンドロビン方式で複数のエージェントを対戦させる。"""

        if num_matches <= 0:
            raise ValueError("num_matches must be positive")

        if len(competitors) < 3:
            raise ValueError("ranking requires at least three competitors")

        if len({competitor.name for competitor in competitors}) != len(competitors):
            raise ValueError("competitor names must be unique")

        # 対戦
        series_results: list[ArenaSeriesResult] = []

        for competitor1, competitor2 in combinations(competitors, 2):
            series_result = self.play_series(
                competitor1,
                competitor2,
                num_matches,
                save_log,
            )
            series_results.append(series_result)

        # 集計
        score_weight = {
            "win_count": (1, 0, 0),  # 勝数重視
            "point": (1, 0, -1),  # 勝ち点重視（勝ち:1, 引き分け:0, 負け:-1）
        }[ranking_method]

        competitor_scores: dict[str, int] = {
            competitor.name: 0 for competitor in competitors
        }

        for series_result in series_results:
            evaluation1, evaluation2 = self.evaluate_series(series_result)
            competitor_scores[evaluation1.competitor_name] += (
                score_weight[0] * evaluation1.win_count[0]
                + score_weight[1] * evaluation1.draw_count[0]
                + score_weight[2] * evaluation1.loss_count[0]
            )
            competitor_scores[evaluation2.competitor_name] += (
                score_weight[0] * evaluation2.win_count[0]
                + score_weight[1] * evaluation2.draw_count[0]
                + score_weight[2] * evaluation2.loss_count[0]
            )

        ranking = tuple(
            sorted(competitor_scores.items(), key=lambda x: x[1], reverse=True)
        )

        return ArenaRoundRobinResult(
            series=tuple(series_results),
            ranking=ranking,
        )

    @staticmethod
    def evaluate_series(
        series_result: ArenaSeriesResult,
    ) -> tuple[CompetitorEvaluation, CompetitorEvaluation]:

        competitor1_first = [
            i
            for i, match in enumerate(series_result.matches)
            if match.first_competitor_name == series_result.competitor1_name
        ]
        competitor2_first = [
            i
            for i, match in enumerate(series_result.matches)
            if match.first_competitor_name == series_result.competitor2_name
        ]

        competitor1_evaluation = CompetitorEvaluation(
            competitor_name=series_result.competitor1_name,
            opponent_name=series_result.competitor2_name,
            matches=series_result.matches,
            first_player_index=tuple(competitor1_first),
            second_player_index=tuple(competitor2_first),
        )

        competitor2_evaluation = CompetitorEvaluation(
            competitor_name=series_result.competitor2_name,
            opponent_name=series_result.competitor1_name,
            matches=series_result.matches,
            first_player_index=tuple(competitor2_first),
            second_player_index=tuple(competitor1_first),
        )

        return competitor1_evaluation, competitor2_evaluation
