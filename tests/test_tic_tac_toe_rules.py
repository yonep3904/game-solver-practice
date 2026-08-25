import pytest

from game_solver.core import GameResult, Player
from game_solver.games.tic_tac_toe import TicTacToeAction, TicTacToeState
from game_solver.games.tic_tac_toe.game import WINNING_LINES, TicTacToeGameRules


@pytest.fixture
def rules() -> TicTacToeGameRules:
    """各テストで使う三目並べの公式ルールを生成する。"""
    return TicTacToeGameRules()


def test_initial_state(rules: TicTacToeGameRules) -> None:
    """初期盤面、先手、合法手、勝敗が正しいことを確認する。"""
    state = rules.initial_state()

    assert state.board == (None,) * 9
    assert rules.current_player(state) is Player.FIRST
    assert rules.legal_actions(state) == [TicTacToeAction(i) for i in range(9)]
    assert not rules.is_terminal(state)
    assert rules.result(state) is None


def test_apply_action_places_stone_and_changes_turn(
    rules: TicTacToeGameRules,
) -> None:
    """着手すると指定マスに石が置かれ、手番が交代することを確認する。"""
    initial = rules.initial_state()
    state = rules.apply_action(initial, TicTacToeAction(4))

    assert initial.board == (None,) * 9
    assert state.board[4] is Player.FIRST
    assert rules.current_player(state) is Player.SECOND
    assert TicTacToeAction(4) not in rules.legal_actions(state)


@pytest.mark.parametrize("line", WINNING_LINES)
@pytest.mark.parametrize(
    ("player", "expected"),
    [(Player.FIRST, GameResult.FIRST), (Player.SECOND, GameResult.SECOND)],
)
def test_all_winning_lines_are_detected(
    rules: TicTacToeGameRules,
    line: tuple[int, int, int],
    player: Player,
    expected: GameResult,
) -> None:
    """両プレイヤーについて縦横斜めの全勝利ラインを検出する。"""
    board: list[Player | None] = [None] * 9
    for position in line:
        board[position] = player
    state = TicTacToeState(tuple(board), player.opponent)

    assert rules.result(state) is expected
    assert rules.is_terminal(state)
    assert rules.legal_actions(state) == []


def test_full_board_without_winner_is_draw(rules: TicTacToeGameRules) -> None:
    """勝者のいない盤面が埋まった場合に引き分けと判定する。"""
    state = TicTacToeState(
        (
            Player.FIRST,
            Player.SECOND,
            Player.FIRST,
            Player.FIRST,
            Player.SECOND,
            Player.SECOND,
            Player.SECOND,
            Player.FIRST,
            Player.FIRST,
        ),
        Player.SECOND,
    )

    assert rules.result(state) is GameResult.DRAW
    assert rules.is_terminal(state)
    assert rules.legal_actions(state) == []


def test_occupied_square_cannot_be_played(rules: TicTacToeGameRules) -> None:
    """公式ルールが使用済みマスへの着手を拒否することを確認する。"""
    state = rules.apply_action(rules.initial_state(), TicTacToeAction(0))

    assert not rules.is_legal_action(state, TicTacToeAction(0))
    with pytest.raises(ValueError, match="Illegal action"):
        rules.apply_action(state, TicTacToeAction(0))


def test_no_action_can_be_played_after_win(rules: TicTacToeGameRules) -> None:
    """公式ルールが勝敗決定後の着手をすべて拒否することを確認する。"""
    state = rules.initial_state()
    for position in (0, 3, 1, 4, 2):
        state = rules.apply_action(state, TicTacToeAction(position))

    assert rules.result(state) is GameResult.FIRST
    assert all(
        not rules.is_legal_action(state, TicTacToeAction(position))
        for position in range(9)
    )
    with pytest.raises(ValueError, match="Illegal action"):
        rules.apply_action(state, TicTacToeAction(5))


@pytest.mark.parametrize("position", [-1, 9])
def test_action_rejects_out_of_range_position(position: int) -> None:
    """盤面外の位置を表すアクションを生成できないことを確認する。"""
    with pytest.raises(ValueError, match="position must be between"):
        TicTacToeAction(position)
