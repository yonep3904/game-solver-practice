from game_solver.core import Player
from game_solver.games.tic_tac_toe import (
    TicTacToeAction,
    TicTacToeAgent,
    TicTacToeGameRules,
    TicTacToeState,
)


class TicTacToeMinimaxAgent(TicTacToeAgent):
    """全ゲーム木を読み、最悪の場合の結果が最善になる手を選ぶ。"""

    def __init__(self) -> None:
        self._rules = TicTacToeGameRules()

    def select_action(self, state: TicTacToeState) -> TicTacToeAction:
        actions = self._rules.legal_actions(state)

        if not actions:
            raise ValueError("No legal actions available.")

        root_player = self._rules.current_player(state)

        # mini-max で最高のスコアを与える手を選ぶ
        return max(
            actions,
            key=lambda action: self._minimax(
                self._rules.apply_action(state, action), root_player
            ),
        )

    def _minimax(self, state: TicTacToeState, root_player: Player) -> int:
        result = self._rules.result(state)

        # ゲームが終了している場合
        if result is not None:
            winner = result.winner
            if winner is root_player:
                return 1
            elif winner is root_player.opponent:
                return -1
            else:
                return 0

        legal_actions = self._rules.legal_actions(state)

        # 次の手が自分の場合は最大化、相手の場合は最小化する
        if state.current_player == root_player:
            best_score = -2

            for action in legal_actions:
                next_state = self._rules.apply_action(state, action)
                score = self._minimax(next_state, root_player)
                best_score = max(best_score, score)
        else:
            best_score = 2

            for action in legal_actions:
                next_state = self._rules.apply_action(state, action)
                score = self._minimax(next_state, root_player)
                best_score = min(best_score, score)

        return best_score
