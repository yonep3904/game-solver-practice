import pytest

from game_solver.core import GameResult, Player
from game_solver.games.connect_four import ConnectFourAction
from game_solver.games.connect_four.constants import BOARD_HEIGHT, BOARD_WIDTH
from game_solver.games.connect_four.game import ConnectFourGameRules


@pytest.fixture
def rules() -> ConnectFourGameRules:
    """各テストで使う四目並べの公式ルールを生成する。"""
    return ConnectFourGameRules()


def play(rules: ConnectFourGameRules, columns: list[int]):
    """指定した列への着手を順番に適用して局面を作る。"""
    state = rules.initial_state()
    for column in columns:
        state = rules.apply_action(state, ConnectFourAction(column))
    return state


def test_initial_state(rules: ConnectFourGameRules) -> None:
    """初期盤面、先手、合法手、勝敗が正しいことを確認する。"""
    state = rules.initial_state()

    assert state.board == (None,) * (BOARD_HEIGHT * BOARD_WIDTH)
    assert rules.current_player(state) is Player.FIRST
    assert rules.legal_actions(state) == [ConnectFourAction(i) for i in range(7)]
    assert not rules.is_terminal(state)
    assert rules.result(state) is None


def test_stones_fall_to_lowest_empty_cell(rules: ConnectFourGameRules) -> None:
    """石が指定列の最下段から順に積まれることを確認する。"""
    initial = rules.initial_state()
    after_first = rules.apply_action(initial, ConnectFourAction(3))
    after_second = rules.apply_action(after_first, ConnectFourAction(3))

    assert initial.board[5 * BOARD_WIDTH + 3] is None
    assert after_first.board[5 * BOARD_WIDTH + 3] is Player.FIRST
    assert after_second.board[4 * BOARD_WIDTH + 3] is Player.SECOND
    assert rules.current_player(after_second) is Player.FIRST


@pytest.mark.parametrize(
    ("columns", "expected"),
    [
        ([0, 0, 1, 1, 2, 2, 3], GameResult.FIRST),
        ([0, 1, 0, 1, 0, 1, 0], GameResult.FIRST),
        ([0, 1, 1, 2, 4, 2, 2, 3, 4, 3, 5, 3, 3], GameResult.FIRST),
        ([3, 2, 2, 1, 4, 1, 1, 0, 4, 0, 5, 0, 0], GameResult.FIRST),
        ([0, 1, 0, 1, 2, 1, 2, 1], GameResult.SECOND),
    ],
    ids=["horizontal", "vertical", "diagonal-up", "diagonal-down", "second"],
)
def test_wins_are_detected(
    rules: ConnectFourGameRules, columns: list[int], expected: GameResult
) -> None:
    """縦横両斜めの四連結と後手の勝利を正しく検出する。"""
    state = play(rules, columns)

    assert rules.result(state) is expected
    assert rules.is_terminal(state)
    assert rules.legal_actions(state) == []


def test_full_column_cannot_be_played(rules: ConnectFourGameRules) -> None:
    """公式ルールが満杯の列への着手を拒否することを確認する。"""
    state = play(rules, [2] * BOARD_HEIGHT)
    action = ConnectFourAction(2)

    assert not rules.is_legal_action(state, action)
    assert action not in rules.legal_actions(state)
    with pytest.raises(ValueError, match="Illegal action"):
        rules.apply_action(state, action)


def test_full_board_without_winner_is_draw(rules: ConnectFourGameRules) -> None:
    """勝者を出さずに盤面が埋まった対局を引き分けと判定する。"""
    columns = [
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
    ]

    state = play(rules, columns)

    assert rules.result(state) is GameResult.DRAW
    assert rules.is_terminal(state)
    assert rules.legal_actions(state) == []


def test_no_action_can_be_played_after_win(rules: ConnectFourGameRules) -> None:
    """公式ルールが勝敗決定後の着手を拒否することを確認する。"""
    state = play(rules, [0, 0, 1, 1, 2, 2, 3])

    assert not rules.is_legal_action(state, ConnectFourAction(4))
    with pytest.raises(ValueError, match="Illegal action"):
        rules.apply_action(state, ConnectFourAction(4))


@pytest.mark.parametrize("column", [-1, BOARD_WIDTH])
def test_action_rejects_out_of_range_column(column: int) -> None:
    """盤面外の列を表すアクションを生成できないことを確認する。"""
    with pytest.raises(ValueError, match="column must be between"):
        ConnectFourAction(column)
