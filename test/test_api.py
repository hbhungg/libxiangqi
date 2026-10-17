import pytest

from libxiangqi import (
  BLACK,
  CHARIOT,
  GENERAL,
  RED,
  SOLDIER,
  STARTING_FEN,
  Board,
  IllegalMoveError,
  InvalidMoveError,
  Move,
  Piece,
  parse_square,
  square,
  square_file,
  square_mirror,
  square_name,
  square_rank,
)


def test_square_helpers():
  assert square(4, 3) == parse_square("e4")
  assert square_name(square(8, 9)) == "i10"
  assert square_file(parse_square("e4")) == 4
  assert square_rank(parse_square("e4")) == 3
  assert square_mirror(parse_square("e1")) == parse_square("e10")


def test_move_uci():
  move = Move.from_uci("e4e5")
  assert move.from_square == parse_square("e4")
  assert move.to_square == parse_square("e5")
  assert move.uci() == "e4e5"
  assert str(move) == "e4e5"
  assert move == Move(parse_square("e4"), parse_square("e5"))
  assert hash(move) == hash(Move(parse_square("e4"), parse_square("e5")))


def test_move_uci_rank_10():
  move = Move.from_uci("e4i10")
  assert move.to_square == parse_square("i10")
  assert move.uci() == "e4i10"
  assert Move.from_uci("i10e4").from_square == parse_square("i10")


def test_move_invalid_uci():
  with pytest.raises(InvalidMoveError):
    Move.from_uci("e4zz")


def test_piece_symbols():
  assert Piece(GENERAL, RED).symbol() == "K"
  assert Piece(GENERAL, BLACK).symbol() == "k"
  assert Piece.from_symbol("R") == Piece(CHARIOT, RED)
  assert Piece.from_symbol("p") == Piece(SOLDIER, BLACK)
  assert str(Piece(CHARIOT, RED)) == "R"


def test_starting_fen():
  board = Board()
  assert board.fen() == STARTING_FEN
  assert board.board_fen() == "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR"


def test_fen_roundtrip():
  board = Board()
  board.push(Move.from_uci("e4e5"))
  board.push(Move.from_uci("e7e6"))
  restored = Board(board.fen())
  assert restored == board
  assert restored.fen() == board.fen()


def test_push_pop_peek():
  board = Board()
  move = Move.from_uci("e4e5")
  board.push(move)
  assert board.turn == BLACK
  assert board.peek() == move
  assert board.ply() == 1
  assert board.pop() == move
  assert board.turn == RED
  assert board.ply() == 0
  with pytest.raises(IndexError):
    board.pop()


def test_move_stack_and_counters():
  board = Board()
  board.push(Move.from_uci("e4e5"))  # red soldier
  assert board.fullmove_number == 1
  assert board.halfmove_clock == 0  # soldier move zeroes the clock
  board.push(Move.from_uci("e7e6"))  # black soldier
  assert board.fullmove_number == 2
  board.push(Move.from_uci("a1a2"))  # red chariot
  assert board.halfmove_clock == 1


def test_legal_moves_generator():
  board = Board()
  assert board.legal_moves.count() == 44
  assert len(board.legal_moves) == 44
  assert Move.from_uci("e4e5") in board.legal_moves
  assert Move.from_uci("e4e6") not in board.legal_moves
  assert bool(board.legal_moves)


def test_piece_access():
  board = Board()
  assert board.piece_at(parse_square("e1")) == Piece(GENERAL, RED)
  assert board.piece_type_at(parse_square("e1")) == GENERAL
  assert board.color_at(parse_square("e1")) == RED
  assert board.piece_at(parse_square("e5")) is None
  assert board.king(RED) == parse_square("e1")
  assert board.king(BLACK) == parse_square("e10")
  assert board.pieces(CHARIOT, RED) == {parse_square("a1"), parse_square("i1")}
  assert board.piece_count() == 32


def test_set_piece_at():
  board = Board()
  board.set_piece_at(parse_square("e5"), Piece(SOLDIER, RED))
  assert board.piece_at(parse_square("e5")) == Piece(SOLDIER, RED)
  board.set_piece_at(parse_square("e5"), None)
  assert board.piece_at(parse_square("e5")) is None
  assert board.remove_piece_at(parse_square("e1")) == Piece(GENERAL, RED)


def test_flying_general_check():
  # Generals facing each other on an open file = check
  board = Board("4k4/9/9/9/9/9/9/9/9/4K4 w - - 0 1")
  assert board.is_check()
  # A piece between the generals blocks the flying general
  board = Board("4k4/9/9/9/9/9/9/9/4P4/4K4 w - - 0 1")
  assert not board.is_check()


def test_cannot_move_into_check():
  board = Board("4k4/9/9/9/9/9/9/9/4P4/4K4 w - - 0 1")
  # Moving the soldier away exposes the flying general -> illegal
  assert not board.is_legal(Move.from_uci("e4e5"))
  with pytest.raises(IllegalMoveError):
    board.make_move(4, 3, 4, 4)


def test_checkmate():
  # Black general at e10, red chariot at a10 checking along the back rank,
  # red soldier at e9 blocking the flying-general capture, red general at e1.
  board = Board("R3k4/4P4/9/9/9/9/9/9/9/4K4 b - - 0 1")
  assert board.is_check()
  assert board.is_checkmate()
  assert board.is_game_over()
  assert board.result() == "1-0"


def test_copy_and_equality():
  board = Board()
  board.push(Move.from_uci("e4e5"))
  clone = board.copy()
  assert clone == board
  assert clone is not board
  clone.push(Move.from_uci("e7e6"))
  assert clone != board
  assert board.ply() == 1


def test_unicode_and_repr():
  board = Board()
  assert "帥" in str(board)
  assert repr(board).startswith("Board('rnbakabnr")


def test_push_uci_and_san():
  board = Board()
  move = Move.from_uci("e4e5")
  assert board.san(move) == "Pe4e5"  # san() uses the current position as context
  assert board.parse_san("Pe4e5") == move
  board.push_uci("e4e5")
  assert board.turn == BLACK


def test_mirror():
  board = Board()
  mirrored = board.mirror()
  # The red general at e1 mirrors to a black general at e10
  assert mirrored.piece_at(parse_square("e10")) == Piece(GENERAL, BLACK)
  assert mirrored.turn == BLACK
