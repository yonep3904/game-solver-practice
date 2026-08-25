import pytest

from game_solver.agents.connect_four.engine import ConnectFourEngine
from game_solver.games.connect_four import ConnectFourAction
from game_solver.games.connect_four.game import ConnectFourGameRules

GAME_SEQUENCES = [
    [],
    [3, 3, 0, 2, 5, 4, 5, 6, 4, 2],
    [0, 0, 1, 1, 2, 2, 3],
    [0, 1, 0, 1, 0, 1, 0],
    [0, 1, 1, 2, 4, 2, 2, 3, 4, 3, 5, 3, 3],
    [3, 2, 2, 1, 4, 1, 1, 0, 4, 0, 5, 0, 0],
    [0, 1, 0, 1, 2, 1, 2, 1],
    [
        3,
        3,
        0,
        2,
        5,
        4,
        5,
        6,
        4,
        2,
        2,
        3,
        3,
        5,
        5,
        2,
        2,
        4,
        3,
        3,
        1,
        1,
        2,
        1,
        5,
        5,
        0,
        4,
        0,
        4,
        4,
        6,
        6,
        6,
        6,
        0,
        1,
        0,
        6,
        0,
        1,
        1,
    ],
]


@pytest.mark.parametrize("columns", GAME_SEQUENCES)
def test_engine_matches_rules_through_complete_games(columns: list[int]) -> None:
    """代表的な対局の全局面で高速エンジンと公式ルールを比較する。"""
    rules = ConnectFourGameRules()
    state = rules.initial_state()
    engine_state = ConnectFourEngine.initial_state()

    for column in [*columns, None]:
        assert ConnectFourEngine.to_state(engine_state) == state
        assert ConnectFourEngine.from_state(state) == engine_state
        assert ConnectFourEngine.current_player(engine_state) is state.current_player
        assert ConnectFourEngine.result(engine_state) is rules.result(state)
        assert ConnectFourEngine.is_terminal(engine_state) is rules.is_terminal(state)

        # 高速エンジンに防御的処理は要求せず、正しい呼び出し順における
        # 公式ルールとの一致だけを保証する。
        if not rules.is_terminal(state):
            assert ConnectFourEngine.legal_actions(engine_state) == [
                ConnectFourEngine.from_action(action)
                for action in rules.legal_actions(state)
            ]

        if column is None:
            break
        action = ConnectFourAction(column)
        engine_action = ConnectFourEngine.from_action(action)
        assert ConnectFourEngine.to_action(engine_action) == action
        state = rules.apply_action(state, action)
        engine_state = ConnectFourEngine.apply_action(engine_state, engine_action)
