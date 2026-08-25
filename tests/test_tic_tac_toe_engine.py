from game_solver.agents.tic_tac_toe.engine import TicTacToeEngine
from game_solver.games.tic_tac_toe import TicTacToeAction
from game_solver.games.tic_tac_toe.game import TicTacToeGameRules


def test_engine_matches_rules_for_every_reachable_state() -> None:
    """全到達可能局面で高速エンジンと公式ルールの挙動を比較する。"""
    rules = TicTacToeGameRules()
    pending = [rules.initial_state()]
    visited = set()

    while pending:
        state = pending.pop()
        if state in visited:
            continue
        visited.add(state)

        engine_state = TicTacToeEngine.from_state(state)
        assert TicTacToeEngine.to_state(engine_state) == state
        assert TicTacToeEngine.current_player(engine_state) is state.current_player
        assert TicTacToeEngine.result(engine_state) is rules.result(state)
        assert TicTacToeEngine.is_terminal(engine_state) is rules.is_terminal(state)

        # 高速エンジンは呼び出し側が終了判定を済ませる前提なので、合法手の
        # 整合性はゲームが続いている局面についてのみ検証する。
        if not rules.is_terminal(state):
            assert TicTacToeEngine.legal_actions(engine_state) == [
                TicTacToeEngine.from_action(action)
                for action in rules.legal_actions(state)
            ]

        for action in rules.legal_actions(state):
            engine_action = TicTacToeEngine.from_action(action)
            assert TicTacToeEngine.to_action(engine_action) == action

            next_state = rules.apply_action(state, action)
            next_engine_state = TicTacToeEngine.apply_action(
                engine_state, engine_action
            )
            assert TicTacToeEngine.to_state(next_engine_state) == next_state
            pending.append(next_state)


def test_initial_states_are_equivalent() -> None:
    """初期状態とアクションの相互変換が公式表現と一致することを確認する。"""
    official = TicTacToeGameRules().initial_state()
    engine = TicTacToeEngine.initial_state()

    assert TicTacToeEngine.to_state(engine) == official
    assert TicTacToeEngine.from_state(official) == engine
    assert TicTacToeEngine.to_action(4) == TicTacToeAction(4)
