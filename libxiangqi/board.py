"""Pure-Python Xiangqi engine with a python-chess-like API.

The board is stored as a 144-cell array: a 12x12 grid with a one-cell
out-of-bounds border, so piece movement never needs explicit bounds checks.
Public squares are 0-89 (``A1`` .. ``I10``), matching python-chess conventions.
"""

from __future__ import annotations

OUT_OF_BOUNDS = 255
EMPTY = 0
RANK_SZ = 10  # Height
FILE_SZ = 9  # Width

# Piece type values (also used as the on-board encoding, low nibble)
GENERAL = 1
ADVISOR = 2
ELEPHANT = 3
HORSE = 4
CHARIOT = 5
CANNON = 6
SOLDIER = 7

# Colors
RED = True
BLACK = False

# --- exceptions -----------------------------------------------------------


class IllegalMoveError(ValueError):
  """Raised when the attempted move is illegal in the current position."""


class InvalidMoveError(ValueError):
  """Raised when move notation is not syntactically valid."""


class AmbiguousMoveError(ValueError):
  """Raised when move notation is ambiguous."""


# Backwards-compatible alias (the original Rust engine raised ``IllegalMove``).
IllegalMove = IllegalMoveError

# --- squares --------------------------------------------------------------

FILE_NAMES = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
RANK_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]


def square(file: int, rank: int) -> int:
  return rank * FILE_SZ + file


def square_file(square: int) -> int:
  return square % FILE_SZ


def square_rank(square: int) -> int:
  return square // FILE_SZ


def square_name(square: int) -> str:
  return FILE_NAMES[square_file(square)] + RANK_NAMES[square_rank(square)]


def parse_square(name: str) -> int:
  if len(name) not in (2, 3):
    raise ValueError(f"invalid square name: {name!r}")
  file = name[0]
  rank = name[1:]
  if file not in FILE_NAMES or rank not in RANK_NAMES:
    raise ValueError(f"invalid square name: {name!r}")
  return square(FILE_NAMES.index(file), RANK_NAMES.index(rank))


def square_mirror(sq: int) -> int:
  return square(square_file(sq), RANK_SZ - 1 - square_rank(sq))


def square_distance(a: int, b: int) -> int:
  return max(abs(square_file(a) - square_file(b)), abs(square_rank(a) - square_rank(b)))


def square_manhattan_distance(a: int, b: int) -> int:
  return abs(square_file(a) - square_file(b)) + abs(square_rank(a) - square_rank(b))


SQUARES = [square(f, r) for r in range(RANK_SZ) for f in range(FILE_SZ)]
SQUARE_NAMES = [square_name(sq) for sq in SQUARES]


def pos_to_idx(file: int, rank: int) -> int | None:
  if file >= FILE_SZ or rank >= RANK_SZ:
    return None
  return (rank + 1) * 12 + (file + 1)


def _idx(file: int, rank: int) -> int:
  """pos_to_idx for known-valid coordinates (internal use)."""
  idx = pos_to_idx(file, rank)
  assert idx is not None
  return idx


def square_to_idx(square: int) -> int:
  return _idx(square_file(square), square_rank(square))


def in_palace(file: int, rank: int, side: bool) -> bool:
  if file < 3 or file > 5:
    return False
  if side == RED:
    return rank <= 2
  return rank >= 7


def crossed_river(rank: int, side: bool) -> bool:
  if side == RED:
    return rank > 4
  return rank < 5


# --- pieces ---------------------------------------------------------------

_FEN_SYMBOLS = {GENERAL: "k", ADVISOR: "a", ELEPHANT: "b", HORSE: "n", CHARIOT: "r", CANNON: "c", SOLDIER: "p"}

_PIECE_NAMES = {
  GENERAL: "general",
  ADVISOR: "advisor",
  ELEPHANT: "elephant",
  HORSE: "horse",
  CHARIOT: "chariot",
  CANNON: "cannon",
  SOLDIER: "soldier",
}

_ASCII_SYMBOLS = {GENERAL: "G", ADVISOR: "A", ELEPHANT: "E", HORSE: "H", CHARIOT: "R", CANNON: "C", SOLDIER: "S"}

_UNICODE_SYMBOLS = {
  (GENERAL, RED): "帥",
  (ADVISOR, RED): "仕",
  (ELEPHANT, RED): "相",
  (HORSE, RED): "馬",
  (CHARIOT, RED): "車",
  (CANNON, RED): "炮",
  (SOLDIER, RED): "兵",
  (GENERAL, BLACK): "將",
  (ADVISOR, BLACK): "士",
  (ELEPHANT, BLACK): "象",
  (HORSE, BLACK): "馬",
  (CHARIOT, BLACK): "車",
  (CANNON, BLACK): "砲",
  (SOLDIER, BLACK): "卒",
}


def piece_symbol(piece_type: int, color: bool | None = None) -> str:
  sym = _FEN_SYMBOLS[piece_type]
  if color is None:
    return sym
  return sym.upper() if color == RED else sym


def piece_name(piece_type: int) -> str:
  return _PIECE_NAMES[piece_type]


def _piece_from_fen_symbol(ch: str) -> Piece | None:
  color = RED if ch.isupper() else BLACK
  lower = ch.lower()
  for piece_type, sym in _FEN_SYMBOLS.items():
    if sym == lower:
      return Piece(piece_type, color)
  return None


class Piece:
  __slots__ = ("piece_type", "color")

  def __init__(self, piece_type: int, color: bool):
    self.piece_type = piece_type
    self.color = color

  def symbol(self) -> str:
    return piece_symbol(self.piece_type, self.color)

  def unicode_symbol(self, *, invert_color: bool = False) -> str:
    color = self.color if not invert_color else not self.color
    return _UNICODE_SYMBOLS[(self.piece_type, color)]

  @classmethod
  def from_symbol(cls, symbol: str) -> Piece:
    piece = _piece_from_fen_symbol(symbol)
    if piece is None:
      raise ValueError(f"invalid piece symbol: {symbol!r}")
    return piece

  def to_u8(self) -> int:
    color_flag = 0 if self.color == RED else 0b00010000
    return self.piece_type | color_flag

  @classmethod
  def from_u8(cls, val: int) -> Piece | None:
    if val == EMPTY or val == OUT_OF_BOUNDS:
      return None
    piece_type = val & 0b00001111
    if piece_type not in _FEN_SYMBOLS:
      return None
    is_black = (val & 0b00010000) != 0
    return cls(piece_type, BLACK if is_black else RED)

  def __eq__(self, other: object) -> bool:
    if isinstance(other, Piece):
      return self.piece_type == other.piece_type and self.color == other.color
    return NotImplemented

  def __hash__(self) -> int:
    return hash((self.piece_type, self.color))

  def __str__(self) -> str:
    return self.symbol()

  def __repr__(self) -> str:
    return f"Piece.from_symbol({self.symbol()!r})"


# --- moves ----------------------------------------------------------------


class Move:
  __slots__ = ("from_square", "to_square")

  def __init__(self, from_square: int, to_square: int):
    self.from_square = from_square
    self.to_square = to_square

  def uci(self) -> str:
    return square_name(self.from_square) + square_name(self.to_square)

  @classmethod
  def from_uci(cls, uci: str) -> Move:
    # Square names are 2 or 3 characters (rank 10 is two digits), so a UCI
    # string is 4, 5 or 6 characters. Try every split into two valid squares.
    for i in range(2, len(uci) - 1):
      try:
        from_square = parse_square(uci[:i])
        to_square = parse_square(uci[i:])
      except ValueError:
        continue
      return cls(from_square, to_square)
    raise InvalidMoveError(f"invalid uci: {uci!r}")

  def __eq__(self, other: object) -> bool:
    if isinstance(other, Move):
      return self.from_square == other.from_square and self.to_square == other.to_square
    return NotImplemented

  def __hash__(self) -> int:
    return hash((self.from_square, self.to_square))

  def __str__(self) -> str:
    return self.uci()

  def __repr__(self) -> str:
    return f"Move.from_uci({self.uci()!r})"


# --- outcomes -------------------------------------------------------------

TERMINATION_CHECKMATE = 1
TERMINATION_STALEMATE = 2
TERMINATION_INSUFFICIENT_MATERIAL = 3
TERMINATION_SIXTY_MOVES = 4
TERMINATION_REPETITION = 5


class Outcome:
  __slots__ = ("winner", "termination", "result")

  def __init__(self, winner: bool | None, termination: int, result: str):
    self.winner = winner
    self.termination = termination
    self.result = result

  def __eq__(self, other: object) -> bool:
    if isinstance(other, Outcome):
      return self.winner == other.winner and self.termination == other.termination and self.result == other.result
    return NotImplemented

  def __repr__(self) -> str:
    return f"Outcome(winner={self.winner!r}, termination={self.termination!r}, result={self.result!r})"


# --- move generators ------------------------------------------------------


class LegalMoveGenerator:
  def __init__(self, board: Board):
    self.board = board

  def __iter__(self):
    return self.board.generate_legal_moves()

  def __len__(self) -> int:
    return sum(1 for _ in self)

  def __bool__(self) -> bool:
    return any(self)

  def __contains__(self, move: object) -> bool:
    return isinstance(move, Move) and self.board.is_legal(move)

  def count(self) -> int:
    return len(self)


class PseudoLegalMoveGenerator:
  def __init__(self, board: Board):
    self.board = board

  def __iter__(self):
    return self.board.generate_pseudo_legal_moves()

  def __len__(self) -> int:
    return sum(1 for _ in self)

  def __bool__(self) -> bool:
    return any(self)

  def __contains__(self, move: object) -> bool:
    return isinstance(move, Move) and self.board.is_pseudo_legal(move)

  def count(self) -> int:
    return len(self)


# --- board ----------------------------------------------------------------

STARTING_BOARD_FEN = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR"
STARTING_FEN = f"{STARTING_BOARD_FEN} w - - 0 1"

STATUS_VALID = 0
STATUS_NO_RED_GENERAL = 1 << 0
STATUS_NO_BLACK_GENERAL = 1 << 1
STATUS_TOO_MANY_GENERALS = 1 << 2
STATUS_OPPOSITE_CHECK = 1 << 3
STATUS_EMPTY = 1 << 4


class Board:
  def __init__(self, fen: str | None = STARTING_FEN):
    self.board = [OUT_OF_BOUNDS] * 144
    self.turn = RED
    self.move_stack: list[Move] = []
    self._undo_stack: list[tuple[int, int, int]] = []
    self._key_stack: list[tuple] = []
    self.halfmove_clock = 0
    self.fullmove_number = 1
    if fen is None:
      self.clear_board()
    else:
      self.set_fen(fen)

  # --- position setup -----------------------------------------------------

  def clear_board(self) -> None:
    self.board = [OUT_OF_BOUNDS] * 144
    for rank in range(RANK_SZ):
      for file in range(FILE_SZ):
        self.board[_idx(file, rank)] = EMPTY

  def clear(self) -> None:
    self.clear_board()
    self.turn = RED
    self.halfmove_clock = 0
    self.fullmove_number = 1
    self.clear_stack()

  def reset(self) -> None:
    self.set_fen(STARTING_FEN)

  def clear_stack(self) -> None:
    self.move_stack.clear()
    self._undo_stack.clear()
    self._key_stack = [self._transposition_key()]

  def set_board_fen(self, fen: str) -> None:
    self.clear_board()
    ranks = fen.split("/")
    if len(ranks) != RANK_SZ:
      raise ValueError(f"expected {RANK_SZ} rows in board fen: {fen!r}")
    for i, rank_str in enumerate(ranks):
      rank = RANK_SZ - 1 - i
      file = 0
      for ch in rank_str:
        if ch.isdigit():
          file += int(ch)
        else:
          piece = _piece_from_fen_symbol(ch)
          if piece is None:
            raise ValueError(f"invalid character in board fen: {ch!r}")
          self.set_piece(file, rank, piece.piece_type, piece.color)
          file += 1
      if file != FILE_SZ:
        raise ValueError(f"invalid board fen: {fen!r}")

  def set_fen(self, fen: str) -> None:
    parts = fen.split()
    if len(parts) != 6:
      raise ValueError(f"expected 6 parts in fen: {fen!r}")
    self.set_board_fen(parts[0])
    self.turn = RED if parts[1] == "w" else BLACK
    self.halfmove_clock = int(parts[4])
    self.fullmove_number = int(parts[5])
    self.clear_stack()

  def board_fen(self) -> str:
    rows = []
    for rank in range(RANK_SZ - 1, -1, -1):
      row = []
      empty = 0
      for file in range(FILE_SZ):
        piece = self.get_piece(file, rank)
        if piece is None:
          empty += 1
        else:
          if empty:
            row.append(str(empty))
            empty = 0
          sym = _FEN_SYMBOLS[piece.piece_type]
          row.append(sym.upper() if piece.color == RED else sym)
      if empty:
        row.append(str(empty))
      rows.append("".join(row))
    return "/".join(rows)

  def fen(self) -> str:
    return f"{self.board_fen()} {'w' if self.turn == RED else 'b'} - - {self.halfmove_clock} {self.fullmove_number}"

  def epd(self, **operations) -> str:
    epd = f"{self.board_fen()} {'w' if self.turn == RED else 'b'} - -"
    if operations:
      parts = []
      for name, value in operations.items():
        if isinstance(value, Move):
          parts.append(f"{name} {value.uci()}")
        elif isinstance(value, (list, tuple)):
          parts.append(f"{name} {' '.join(m.uci() for m in value)}")
        elif value is None:
          parts.append(f"{name} -")
        else:
          parts.append(f"{name} {value}")
      epd += " " + "; ".join(parts) + ";"
    return epd

  def set_epd(self, epd: str) -> dict:
    parts = epd.split()
    if len(parts) < 4:
      raise ValueError(f"invalid epd: {epd!r}")
    self.set_board_fen(parts[0])
    self.turn = RED if parts[1] == "w" else BLACK
    self.halfmove_clock = 0
    self.fullmove_number = 1
    self.clear_stack()
    operations: dict = {}
    rest = epd.split(None, 4)
    if len(rest) > 4 and rest[4].strip():
      for op in rest[4].split(";"):
        op = op.strip()
        if not op:
          continue
        name, _, value = op.partition(" ")
        operations[name] = value
    return operations

  # --- piece access -------------------------------------------------------

  def set_piece(self, file: int, rank: int, piece_type: int, side: bool) -> None:
    idx = pos_to_idx(file, rank)
    if idx is None:
      return None
    self.board[idx] = Piece(piece_type, side).to_u8()
    return None

  def get_piece(self, file: int, rank: int) -> Piece | None:
    idx = pos_to_idx(file, rank)
    if idx is None:
      return None
    return Piece.from_u8(self.board[idx])

  def piece_at(self, square: int) -> Piece | None:
    return Piece.from_u8(self.board[square_to_idx(square)])

  def piece_type_at(self, square: int) -> int | None:
    piece = self.piece_at(square)
    return piece.piece_type if piece is not None else None

  def color_at(self, square: int) -> bool | None:
    piece = self.piece_at(square)
    return piece.color if piece is not None else None

  def set_piece_at(self, square: int, piece: Piece | None) -> None:
    idx = square_to_idx(square)
    if piece is None:
      self.board[idx] = EMPTY
    else:
      self.board[idx] = piece.to_u8()

  def remove_piece_at(self, square: int) -> Piece | None:
    piece = self.piece_at(square)
    self.board[square_to_idx(square)] = EMPTY
    return piece

  def pieces(self, piece_type: int, color: bool) -> set[int]:
    return {sq for sq in self._piece_squares(color) if (piece := self.piece_at(sq)) is not None and piece.piece_type == piece_type}

  def piece_map(self) -> dict[int, Piece]:
    return {sq: piece for sq in SQUARES if (piece := self.piece_at(sq)) is not None}

  def piece_count(self) -> int:
    return sum(1 for sq in SQUARES if self.piece_at(sq) is not None)

  def king(self, color: bool) -> int | None:
    generals = self.pieces(GENERAL, color)
    if len(generals) == 1:
      return next(iter(generals))
    return None

  def _piece_squares(self, color: bool) -> set[int]:
    result = set()
    for rank in range(RANK_SZ):
      for file in range(FILE_SZ):
        piece = self.get_piece(file, rank)
        if piece is not None and piece.color == color:
          result.add(square(file, rank))
    return result

  # --- move validation ----------------------------------------------------

  def is_valid_general_move(self, from_file: int, from_rank: int, to_file: int, to_rank: int, side: bool) -> bool:
    # Flying general: capture the enemy general along an open file
    if to_file == from_file:
      dest = self.get_piece(to_file, to_rank)
      if dest is not None and dest.piece_type == GENERAL and dest.color != side:
        if self._path_clear(from_file, from_rank, to_rank):
          return True
    # Must stay in palace
    if not in_palace(to_file, to_rank, side):
      return False
    # Can only move one step orthogonally
    file_diff = abs(from_file - to_file)
    rank_diff = abs(from_rank - to_rank)
    return (file_diff == 1 and rank_diff == 0) or (file_diff == 0 and rank_diff == 1)

  def is_valid_advisor_move(self, from_file: int, from_rank: int, to_file: int, to_rank: int, side: bool) -> bool:
    if not in_palace(to_file, to_rank, side):
      return False
    file_diff = abs(from_file - to_file)
    rank_diff = abs(from_rank - to_rank)
    return file_diff == 1 and rank_diff == 1

  def is_valid_elephant_move(self, from_file: int, from_rank: int, to_file: int, to_rank: int, side: bool) -> bool:
    if side == RED:
      if to_rank > 4:
        return False
    else:
      if to_rank < 5:
        return False
    file_diff = from_file - to_file
    rank_diff = from_rank - to_rank
    if abs(file_diff) != 2 or abs(rank_diff) != 2:
      return False
    mid_file = (from_file + to_file) // 2
    mid_rank = (from_rank + to_rank) // 2
    return self.board[_idx(mid_file, mid_rank)] == EMPTY

  def is_valid_horse_move(self, from_file: int, from_rank: int, to_file: int, to_rank: int) -> bool:
    file_diff = abs(from_file - to_file)
    rank_diff = abs(from_rank - to_rank)
    if not ((file_diff == 1 and rank_diff == 2) or (file_diff == 2 and rank_diff == 1)):
      return False
    if file_diff == 2:
      block_file = (from_file + to_file) // 2
      block_rank = from_rank
    else:
      block_file = from_file
      block_rank = (from_rank + to_rank) // 2
    return self.board[_idx(block_file, block_rank)] == EMPTY

  def is_valid_chariot_move(self, from_file: int, from_rank: int, to_file: int, to_rank: int) -> bool:
    if from_file != to_file and from_rank != to_rank:
      return False
    if from_file == to_file:
      if from_rank < to_rank:
        start, end = from_rank + 1, to_rank
      else:
        start, end = to_rank + 1, from_rank
      for rank in range(start, end):
        if self.board[_idx(from_file, rank)] != EMPTY:
          return False
    else:
      if from_file < to_file:
        start, end = from_file + 1, to_file
      else:
        start, end = to_file + 1, from_file
      for file in range(start, end):
        if self.board[_idx(file, from_rank)] != EMPTY:
          return False
    return True

  def is_valid_cannon_move(self, from_file: int, from_rank: int, to_file: int, to_rank: int, is_capture: bool) -> bool:
    if from_file != to_file and from_rank != to_rank:
      return False
    pieces_between = 0
    if from_file == to_file:
      if from_rank < to_rank:
        start, end = from_rank + 1, to_rank
      else:
        start, end = to_rank + 1, from_rank
      for rank in range(start, end):
        if self.board[_idx(from_file, rank)] != EMPTY:
          pieces_between += 1
    else:
      if from_file < to_file:
        start, end = from_file + 1, to_file
      else:
        start, end = to_file + 1, from_file
      for file in range(start, end):
        if self.board[_idx(file, from_rank)] != EMPTY:
          pieces_between += 1
    if is_capture:
      return pieces_between == 1
    return pieces_between == 0

  def is_valid_soldier_move(self, from_file: int, from_rank: int, to_file: int, to_rank: int, side: bool) -> bool:
    file_diff = abs(from_file - to_file)
    rank_diff = from_rank - to_rank
    has_crossed = crossed_river(from_rank, side)
    if side == RED:
      if rank_diff == -1 and file_diff == 0:
        return True
      if has_crossed and rank_diff == 0 and file_diff == 1:
        return True
      return False
    else:
      if rank_diff == 1 and file_diff == 0:
        return True
      if has_crossed and rank_diff == 0 and file_diff == 1:
        return True
      return False

  def _is_valid_move(self, piece: Piece, from_file: int, from_rank: int, to_file: int, to_rank: int, is_capture: bool) -> bool:
    if piece.piece_type == GENERAL:
      return self.is_valid_general_move(from_file, from_rank, to_file, to_rank, piece.color)
    if piece.piece_type == ADVISOR:
      return self.is_valid_advisor_move(from_file, from_rank, to_file, to_rank, piece.color)
    if piece.piece_type == ELEPHANT:
      return self.is_valid_elephant_move(from_file, from_rank, to_file, to_rank, piece.color)
    if piece.piece_type == HORSE:
      return self.is_valid_horse_move(from_file, from_rank, to_file, to_rank)
    if piece.piece_type == CHARIOT:
      return self.is_valid_chariot_move(from_file, from_rank, to_file, to_rank)
    if piece.piece_type == CANNON:
      return self.is_valid_cannon_move(from_file, from_rank, to_file, to_rank, is_capture)
    if piece.piece_type == SOLDIER:
      return self.is_valid_soldier_move(from_file, from_rank, to_file, to_rank, piece.color)
    return False

  def _path_clear(self, file: int, rank1: int, rank2: int) -> bool:
    lo, hi = sorted((rank1, rank2))
    return all(self.board[_idx(file, r)] == EMPTY for r in range(lo + 1, hi))

  # --- attacks and check --------------------------------------------------

  def attacks(self, square: int) -> set[int]:
    piece = self.piece_at(square)
    if piece is None:
      return set()
    from_file, from_rank = square_file(square), square_rank(square)
    result = set()
    for to_square in SQUARES:
      to_file, to_rank = square_file(to_square), square_rank(to_square)
      if self._is_valid_move(piece, from_file, from_rank, to_file, to_rank, is_capture=True):
        result.add(to_square)
    return result

  def attackers(self, color: bool, square: int) -> set[int]:
    to_file, to_rank = square_file(square), square_rank(square)
    result = set()
    for from_square in self._piece_squares(color):
      piece = self.piece_at(from_square)
      assert piece is not None
      from_file, from_rank = square_file(from_square), square_rank(from_square)
      if self._is_valid_move(piece, from_file, from_rank, to_file, to_rank, is_capture=True):
        result.add(from_square)
    # Flying general: a general attacks the enemy general along an open file
    target = self.piece_at(square)
    if target is not None and target.piece_type == GENERAL and target.color != color:
      my_general = self.king(color)
      if my_general is not None:
        gf, gr = square_file(my_general), square_rank(my_general)
        if gf == to_file and self._path_clear(gf, gr, to_rank):
          result.add(my_general)
    return result

  def is_attacked_by(self, color: bool, square: int) -> bool:
    return bool(self.attackers(color, square))

  def checkers(self) -> set[int]:
    king_sq = self.king(self.turn)
    if king_sq is None:
      return set()
    return self.attackers(not self.turn, king_sq)

  def is_check(self) -> bool:
    return bool(self.checkers())

  def gives_check(self, move: Move) -> bool:
    self.push(move)
    try:
      return self.is_check()
    finally:
      self.pop()

  def gives_checkmate(self, move: Move) -> bool:
    self.push(move)
    try:
      return self.is_checkmate()
    finally:
      self.pop()

  # --- move making --------------------------------------------------------

  def push(self, move: Move) -> None:
    from_idx = square_to_idx(move.from_square)
    to_idx = square_to_idx(move.to_square)
    captured = self.board[to_idx]
    piece = Piece.from_u8(self.board[from_idx])
    self._undo_stack.append((captured, self.halfmove_clock, self.fullmove_number))
    self.board[to_idx] = self.board[from_idx]
    self.board[from_idx] = EMPTY
    self.move_stack.append(move)
    self.turn = not self.turn
    if captured != EMPTY or (piece is not None and piece.piece_type == SOLDIER):
      self.halfmove_clock = 0
    else:
      self.halfmove_clock += 1
    if self.turn == RED:
      self.fullmove_number += 1
    self._key_stack.append(self._transposition_key())

  def pop(self) -> Move:
    if not self.move_stack:
      raise IndexError("pop from an empty move stack")
    move = self.move_stack.pop()
    captured, prev_halfmove, prev_fullmove = self._undo_stack.pop()
    from_idx = square_to_idx(move.from_square)
    to_idx = square_to_idx(move.to_square)
    self.board[from_idx] = self.board[to_idx]
    self.board[to_idx] = captured
    self.turn = not self.turn
    self.halfmove_clock = prev_halfmove
    self.fullmove_number = prev_fullmove
    self._key_stack.pop()
    return move

  def peek(self) -> Move:
    if not self.move_stack:
      raise IndexError("peek from an empty move stack")
    return self.move_stack[-1]

  def ply(self) -> int:
    return len(self.move_stack)

  def root(self) -> Board:
    return self.copy(stack=False)

  def make_move(self, from_file: int, from_rank: int, to_file: int, to_rank: int) -> None:
    if from_file >= FILE_SZ or from_rank >= RANK_SZ:
      raise IllegalMoveError(f"Invalid from position ({from_file}, {from_rank})")
    if to_file >= FILE_SZ or to_rank >= RANK_SZ:
      raise IllegalMoveError(f"Invalid to position ({to_file}, {to_rank})")
    move = Move(square(from_file, from_rank), square(to_file, to_rank))
    if not self.is_legal(move):
      piece = self.get_piece(from_file, from_rank)
      if piece is None:
        raise IllegalMoveError(f"({from_file}, {from_rank}) has no piece")
      if piece.color != self.turn:
        raise IllegalMoveError("Not turn")
      dest = self.get_piece(to_file, to_rank)
      if dest is not None and dest.color == piece.color:
        raise IllegalMoveError("Cannot capture own piece")
      raise IllegalMoveError(f"Invalid move for {piece.piece_type}")
    self.push(move)

  def is_pseudo_legal(self, move: Move) -> bool:
    piece = self.piece_at(move.from_square)
    if piece is None or piece.color != self.turn:
      return False
    dest = self.piece_at(move.to_square)
    if dest is not None and dest.color == piece.color:
      return False
    is_capture = dest is not None
    return self._is_valid_move(
      piece, square_file(move.from_square), square_rank(move.from_square), square_file(move.to_square), square_rank(move.to_square), is_capture
    )

  def is_legal(self, move: Move) -> bool:
    return self.is_pseudo_legal(move) and not self._is_into_check(move)

  def _is_into_check(self, move: Move) -> bool:
    self.push(move)
    try:
      king_sq = self.king(not self.turn)
      return king_sq is not None and bool(self.attackers(self.turn, king_sq))
    finally:
      self.pop()

  def find_move(self, from_square: int, to_square: int) -> Move:
    move = Move(from_square, to_square)
    if self.is_legal(move):
      return move
    raise IllegalMoveError(f"no legal move from {square_name(from_square)} to {square_name(to_square)}")

  def is_capture(self, move: Move) -> bool:
    return self.piece_at(move.to_square) is not None

  def is_zeroing(self, move: Move) -> bool:
    piece = self.piece_at(move.from_square)
    return self.is_capture(move) or (piece is not None and piece.piece_type == SOLDIER)

  def is_irreversible(self, move: Move) -> bool:
    return self.is_zeroing(move)

  # --- move generation ----------------------------------------------------

  def generate_pseudo_legal_moves(self):
    for from_square in self._piece_squares(self.turn):
      piece = self.piece_at(from_square)
      from_file, from_rank = square_file(from_square), square_rank(from_square)
      for to_square in SQUARES:
        to_file, to_rank = square_file(to_square), square_rank(to_square)
        dest = self.get_piece(to_file, to_rank)
        if dest is not None and dest.color == piece.color:
          continue
        is_capture = dest is not None
        if self._is_valid_move(piece, from_file, from_rank, to_file, to_rank, is_capture):
          yield Move(from_square, to_square)

  def generate_legal_moves(self):
    for move in self.generate_pseudo_legal_moves():
      if self.is_legal(move):
        yield move

  def get_legal_moves(self) -> list[tuple[int, int, int, int]]:
    return [
      (square_file(m.from_square), square_rank(m.from_square), square_file(m.to_square), square_rank(m.to_square))
      for m in self.generate_legal_moves()
    ]

  @property
  def legal_moves(self) -> LegalMoveGenerator:
    return LegalMoveGenerator(self)

  @property
  def pseudo_legal_moves(self) -> PseudoLegalMoveGenerator:
    return PseudoLegalMoveGenerator(self)

  # --- game end -----------------------------------------------------------

  def is_checkmate(self) -> bool:
    if not self.is_check():
      return False
    return not any(self.generate_legal_moves())

  def is_stalemate(self) -> bool:
    if self.is_check():
      return False
    return not any(self.generate_legal_moves())

  def is_insufficient_material(self) -> bool:
    return False

  def has_insufficient_material(self, color: bool) -> bool:
    return False

  def is_sixty_moves(self) -> bool:
    return self.halfmove_clock >= 120

  def is_repetition(self, count: int = 3) -> bool:
    return self._key_stack.count(self._transposition_key()) >= count

  def can_claim_draw(self) -> bool:
    return self.is_sixty_moves() or self.is_repetition(3)

  def is_game_over(self, *, claim_draw: bool = False) -> bool:
    if self.king(RED) is None or self.king(BLACK) is None:
      return True
    if self.is_checkmate() or self.is_stalemate():
      return True
    if claim_draw and self.can_claim_draw():
      return True
    return False

  def result(self, *, claim_draw: bool = False) -> str:
    if self.king(RED) is None:
      return "0-1"
    if self.king(BLACK) is None:
      return "1-0"
    if self.is_checkmate() or self.is_stalemate():
      # In xiangqi, the player who cannot move loses.
      return "0-1" if self.turn == RED else "1-0"
    if claim_draw and self.can_claim_draw():
      return "1/2-1/2"
    return "*"

  def outcome(self, *, claim_draw: bool = False) -> Outcome | None:
    if self.king(RED) is None:
      return Outcome(BLACK, TERMINATION_CHECKMATE, "0-1")
    if self.king(BLACK) is None:
      return Outcome(RED, TERMINATION_CHECKMATE, "1-0")
    if self.is_checkmate():
      return Outcome(not self.turn, TERMINATION_CHECKMATE, self.result())
    if self.is_stalemate():
      return Outcome(not self.turn, TERMINATION_STALEMATE, self.result())
    if claim_draw and self.can_claim_draw():
      return Outcome(None, TERMINATION_REPETITION, "1/2-1/2")
    return None

  # --- notation -----------------------------------------------------------

  def uci(self, move: Move, *, chess960: bool | None = None) -> str:
    return move.uci()

  def parse_uci(self, uci: str) -> Move:
    move = Move.from_uci(uci)
    if not self.is_legal(move):
      raise IllegalMoveError(f"illegal uci: {uci!r} in {self.fen()}")
    return move

  def push_uci(self, uci: str) -> Move:
    move = self.parse_uci(uci)
    self.push(move)
    return move

  def lan(self, move: Move) -> str:
    piece = self.piece_at(move.from_square)
    if piece is None:
      raise ValueError(f"no piece on {square_name(move.from_square)}")
    return piece.symbol() + move.uci()

  def san(self, move: Move) -> str:
    return self.lan(move)

  def parse_san(self, san: str) -> Move:
    try:
      return self.parse_uci(san)
    except (InvalidMoveError, IllegalMoveError):
      pass
    if len(san) == 5:
      try:
        move = Move.from_uci(san[1:])
        if self.is_legal(move):
          return move
      except InvalidMoveError:
        pass
    raise InvalidMoveError(f"invalid san: {san!r}")

  def push_san(self, san: str) -> Move:
    move = self.parse_san(san)
    self.push(move)
    return move

  def variation_san(self, variation) -> str:
    board = self.copy(stack=False)
    san_moves = []
    for move in variation:
      san_moves.append(board.san(move))
      board.push(move)
    return " ".join(san_moves)

  # --- display ------------------------------------------------------------

  def ascii(self) -> str:
    output: list[str] = []
    for rank in range(RANK_SZ - 1, -1, -1):
      for file in range(FILE_SZ):
        idx = _idx(file, rank)
        piece_val = self.board[idx]
        if piece_val == EMPTY:
          symbol = "."
        elif piece_val == OUT_OF_BOUNDS:
          symbol = "X"
        else:
          piece = Piece.from_u8(piece_val)
          if piece is None:
            symbol = "?"
          else:
            base = _ASCII_SYMBOLS[piece.piece_type]
            symbol = base if piece.color == RED else base.lower()
        output.append(symbol)
        output.append(" ")
      output.append("\n")
    output.append("\n")
    return "".join(output)

  def unicode(self, *, invert_color: bool = False, borders: bool = False, empty_square: str = "·", orientation: bool = True) -> str:
    lines = []
    ranks = range(RANK_SZ - 1, -1, -1) if orientation else range(RANK_SZ)
    for rank in ranks:
      row = []
      for file in range(FILE_SZ):
        piece = self.get_piece(file, rank)
        if piece is None:
          row.append(empty_square)
        else:
          color = piece.color if not invert_color else not piece.color
          row.append(_UNICODE_SYMBOLS[(piece.piece_type, color)])
      lines.append(" ".join(row))
    return "\n".join(lines)

  def __str__(self) -> str:
    return self.unicode()

  def __repr__(self) -> str:
    return f"Board('{self.fen()}')"

  def __bool__(self) -> bool:
    return not self.is_game_over(claim_draw=True)

  # --- copying and comparison ---------------------------------------------

  def copy(self, *, stack: bool | int = True) -> Board:
    board = Board(None)
    board.board = self.board.copy()
    board.turn = self.turn
    board.halfmove_clock = self.halfmove_clock
    board.fullmove_number = self.fullmove_number
    if stack:
      board.move_stack = self.move_stack.copy()
      board._undo_stack = self._undo_stack.copy()
      board._key_stack = self._key_stack.copy()
    else:
      board.move_stack = []
      board._undo_stack = []
      board._key_stack = [board._transposition_key()]
    return board

  def __copy__(self) -> Board:
    return self.copy()

  def mirror(self) -> Board:
    board = Board(None)
    for rank in range(RANK_SZ):
      for file in range(FILE_SZ):
        piece = self.get_piece(file, rank)
        if piece is not None:
          board.set_piece(file, RANK_SZ - 1 - rank, piece.piece_type, not piece.color)
    board.turn = not self.turn
    board.halfmove_clock = self.halfmove_clock
    board.fullmove_number = self.fullmove_number
    return board

  def _transposition_key(self) -> tuple:
    return (tuple(self.board), self.turn)

  def __eq__(self, other: object) -> bool:
    if isinstance(other, Board):
      return (
        self.board == other.board
        and self.turn == other.turn
        and self.halfmove_clock == other.halfmove_clock
        and self.fullmove_number == other.fullmove_number
      )
    return NotImplemented

  def __hash__(self) -> int:
    return hash((tuple(self.board), self.turn, self.halfmove_clock, self.fullmove_number))

  # --- validity -----------------------------------------------------------

  def status(self) -> int:
    status = STATUS_VALID
    red_generals = self.pieces(GENERAL, RED)
    black_generals = self.pieces(GENERAL, BLACK)
    if not red_generals:
      status |= STATUS_NO_RED_GENERAL
    elif len(red_generals) > 1:
      status |= STATUS_TOO_MANY_GENERALS
    if not black_generals:
      status |= STATUS_NO_BLACK_GENERAL
    elif len(black_generals) > 1:
      status |= STATUS_TOO_MANY_GENERALS
    if not red_generals and not black_generals:
      status |= STATUS_EMPTY
    if red_generals and black_generals:
      red_general = next(iter(red_generals))
      black_general = next(iter(black_generals))
      if self.turn == RED and self._is_attacked_by(RED, black_general):
        status |= STATUS_OPPOSITE_CHECK
      if self.turn == BLACK and self._is_attacked_by(BLACK, red_general):
        status |= STATUS_OPPOSITE_CHECK
    return status

  def is_valid(self) -> bool:
    return self.status() == STATUS_VALID

  def _is_attacked_by(self, color: bool, square: int) -> bool:
    return bool(self.attackers(color, square))

  # --- web ui -------------------------------------------------------------

  def serve(self, port: int = 9999):
    from http.server import BaseHTTPRequestHandler
    from socketserver import TCPServer
    import json
    import os

    STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

    class TCPServerWithReuse(TCPServer):
      allow_reuse_address = True

      def __init__(self, server_address, RequestHandlerClass):
        print(f"started server on http://127.0.0.1:{server_address[1]}")
        super().__init__(server_address, RequestHandlerClass)

    class Handler(BaseHTTPRequestHandler):
      def send_data(self, data: bytes, content_type: str = "application/json", status_code: int = 200):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        return self.wfile.write(data)

      def do_GET(self):
        from urllib.parse import urlparse

        url = urlparse(self.path)
        match url.path:
          case "/" | "/index.html":
            with open(os.path.join(STATIC_DIR, "index.html"), "rb") as f:
              ret = f.read()
            self.send_data(ret, "text/html", 200)

          case path if path.startswith(("/assets/", "/js/", "/img/")) and "/.." not in path:
            try:
              with open(os.path.join(STATIC_DIR, self.path.strip("/")), "rb") as f:
                ret = f.read()
              if url.path.endswith(".js"):
                content_type = "application/javascript"
              if url.path.endswith(".css"):
                content_type = "text/css"
              if url.path.endswith(".svg"):
                content_type = "image/svg+xml"
              status_code = 200
            except FileNotFoundError:
              status_code = 404
            self.send_data(ret, content_type, status_code)

          case _:
            self.send_response(404)
            self.end_headers()

      def do_POST(self):
        from urllib.parse import urlparse

        url = urlparse(self.path)
        match url.path:
          case "/move":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
              move_data = json.loads(body.decode())
              print(f"Move received: {move_data}")

              response = {"status": "ok", "valid": True}
              ret = json.dumps(response).encode()
              self.send_data(ret, "application/json", 200)
            except Exception as e:
              print(f"Error processing move: {e}")
              response = {"status": "error", "message": str(e)}
              ret = json.dumps(response).encode()
              self.send_data(ret, "application/json", 400)

          case _:
            self.send_response(404)
            self.end_headers()

    server = TCPServerWithReuse(("", port), Handler)
    try:
      server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
      print("libxiangqi server shutdown...")
