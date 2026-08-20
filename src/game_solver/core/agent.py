from __future__ import annotations

from abc import ABC, abstractmethod


class Agent[StateT, ActionT](ABC):
    @abstractmethod
    def select_action(self, state: StateT) -> ActionT:
        """状態に基づいて行動を選択する。"""
        ...
