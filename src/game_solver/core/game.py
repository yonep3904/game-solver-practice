from __future__ import annotations

from abc import ABC, abstractmethod

from .types import GameResult, Player


class GameRules[StateT, ActionT](ABC):
    """ゲームのルールを定義する抽象クラス。

    このクラスが公式のルールとなるため、複雑な最適化よりも正確性・安全性を重視する。

    このクラスが生成する到達可能な状態について、以下が常に成立する。
        is_terminal(state) == (result(state) is not None)
    """

    @abstractmethod
    def initial_state(self) -> StateT:
        """初期状態を返す。"""
        ...

    @abstractmethod
    def is_legal_action(self, state: StateT, action: ActionT) -> bool:
        """指定されたアクションが合法かどうかを返す。

        終了状態では常に False を返す。
        """
        ...

    @abstractmethod
    def apply_action(self, state: StateT, action: ActionT) -> StateT:
        """アクションを適用し、新しい状態を返す。

        raises:
            ValueError: アクションが合法でない場合。
        """
        ...

    @abstractmethod
    def is_terminal(self, state: StateT) -> bool:
        """ゲームが終了しているかどうかを返す。"""
        ...

    @abstractmethod
    def current_player(self, state: StateT) -> Player:
        """現在の状態での手番のプレイヤーを返す。

        raises:
            ValueError: 終了状態の場合。
        """
        ...

    @abstractmethod
    def result(self, state: StateT) -> GameResult | None:
        """勝者または引き分けを返す。ゲームが終了していない場合は None を返す。"""
        ...
