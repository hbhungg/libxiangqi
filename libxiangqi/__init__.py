from typing import Literal, TypeAlias

from .board import (
  ADVISOR,
  BLACK,
  CANNON,
  CHARIOT,
  ELEPHANT,
  GENERAL,
  HORSE,
  RED,
  SOLDIER,
  STATUS_EMPTY,
  STATUS_NO_BLACK_GENERAL,
  STATUS_NO_RED_GENERAL,
  STATUS_OPPOSITE_CHECK,
  STATUS_TOO_MANY_GENERALS,
  STATUS_VALID,
  STARTING_BOARD_FEN,
  STARTING_FEN,
  TERMINATION_CHECKMATE,
  TERMINATION_INSUFFICIENT_MATERIAL,
  TERMINATION_REPETITION,
  TERMINATION_SIXTY_MOVES,
  TERMINATION_STALEMATE,
  AmbiguousMoveError,
  Board,
  IllegalMove,
  IllegalMoveError,
  InvalidMoveError,
  LegalMoveGenerator,
  Move,
  Outcome,
  Piece,
  PseudoLegalMoveGenerator,
  parse_square,
  piece_name,
  piece_symbol,
  square,
  square_distance,
  square_file,
  square_manhattan_distance,
  square_mirror,
  square_name,
  square_rank,
)

Color: TypeAlias = bool
COLORS: list[Color] = [RED, BLACK]
ColorName = Literal["red", "black"]
COLOR_NAMES: list[ColorName] = ["black", "red"]

PieceType: TypeAlias = int
PIECE_TYPES: list[PieceType] = [GENERAL, ADVISOR, ELEPHANT, HORSE, CHARIOT, CANNON, SOLDIER]
PIECE_SYMBOLS = [None, "k", "a", "b", "n", "r", "c", "p"]
PIECE_NAMES = [None, "general", "advisor", "elephant", "horse", "chariot", "cannon", "soldier"]

File: TypeAlias = int
FILE_A: File = 0
FILE_B: File = 1
FILE_C: File = 2
FILE_D: File = 3
FILE_E: File = 4
FILE_F: File = 5
FILE_G: File = 6
FILE_H: File = 7
FILE_I: File = 8
FILES = [FILE_A, FILE_B, FILE_C, FILE_D, FILE_E, FILE_F, FILE_G, FILE_H, FILE_I]
FILE_NAMES = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]

Rank: TypeAlias = int
RANK_1: Rank = 0
RANK_2: Rank = 1
RANK_3: Rank = 2
RANK_4: Rank = 3
RANK_5: Rank = 4
RANK_6: Rank = 5
RANK_7: Rank = 6
RANK_8: Rank = 7
RANK_9: Rank = 8
RANK_10: Rank = 9
RANKS = [RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8, RANK_9, RANK_10]
RANK_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

Square: TypeAlias = int
A1: Square = 0
B1: Square = 1
C1: Square = 2
D1: Square = 3
E1: Square = 4
F1: Square = 5
G1: Square = 6
H1: Square = 7
I1: Square = 8
A2: Square = 9
B2: Square = 10
C2: Square = 11
D2: Square = 12
E2: Square = 13
F2: Square = 14
G2: Square = 15
H2: Square = 16
I2: Square = 17
A3: Square = 18
B3: Square = 19
C3: Square = 20
D3: Square = 21
E3: Square = 22
F3: Square = 23
G3: Square = 24
H3: Square = 25
I3: Square = 26
A4: Square = 27
B4: Square = 28
C4: Square = 29
D4: Square = 30
E4: Square = 31
F4: Square = 32
G4: Square = 33
H4: Square = 34
I4: Square = 35
A5: Square = 36
B5: Square = 37
C5: Square = 38
D5: Square = 39
E5: Square = 40
F5: Square = 41
G5: Square = 42
H5: Square = 43
I5: Square = 44
A6: Square = 45
B6: Square = 46
C6: Square = 47
D6: Square = 48
E6: Square = 49
F6: Square = 50
G6: Square = 51
H6: Square = 52
I6: Square = 53
A7: Square = 54
B7: Square = 55
C7: Square = 56
D7: Square = 57
E7: Square = 58
F7: Square = 59
G7: Square = 60
H7: Square = 61
I7: Square = 62
A8: Square = 63
B8: Square = 64
C8: Square = 65
D8: Square = 66
E8: Square = 67
F8: Square = 68
G8: Square = 69
H8: Square = 70
I8: Square = 71
A9: Square = 72
B9: Square = 73
C9: Square = 74
D9: Square = 75
E9: Square = 76
F9: Square = 77
G9: Square = 78
H9: Square = 79
I9: Square = 80
A10: Square = 81
B10: Square = 82
C10: Square = 83
D10: Square = 84
E10: Square = 85
F10: Square = 86
G10: Square = 87
H10: Square = 88
I10: Square = 89

SQUARES = list(range(90))
SQUARE_NAMES = [square_name(sq) for sq in SQUARES]

__all__ = [
  "ADVISOR",
  "BLACK",
  "CANNON",
  "CHARIOT",
  "COLOR_NAMES",
  "COLORS",
  "ELEPHANT",
  "FILE_A",
  "FILE_B",
  "FILE_C",
  "FILE_D",
  "FILE_E",
  "FILE_F",
  "FILE_G",
  "FILE_H",
  "FILE_I",
  "FILE_NAMES",
  "FILES",
  "GENERAL",
  "HORSE",
  "IllegalMove",
  "IllegalMoveError",
  "InvalidMoveError",
  "AmbiguousMoveError",
  "LegalMoveGenerator",
  "Move",
  "Outcome",
  "PIECE_NAMES",
  "PIECE_SYMBOLS",
  "PIECE_TYPES",
  "Piece",
  "PseudoLegalMoveGenerator",
  "RANK_1",
  "RANK_10",
  "RANK_2",
  "RANK_3",
  "RANK_4",
  "RANK_5",
  "RANK_6",
  "RANK_7",
  "RANK_8",
  "RANK_9",
  "RANK_NAMES",
  "RANKS",
  "RED",
  "SOLDIER",
  "SQUARES",
  "SQUARE_NAMES",
  "STARTING_BOARD_FEN",
  "STARTING_FEN",
  "STATUS_EMPTY",
  "STATUS_NO_BLACK_GENERAL",
  "STATUS_NO_RED_GENERAL",
  "STATUS_OPPOSITE_CHECK",
  "STATUS_TOO_MANY_GENERALS",
  "STATUS_VALID",
  "TERMINATION_CHECKMATE",
  "TERMINATION_INSUFFICIENT_MATERIAL",
  "TERMINATION_REPETITION",
  "TERMINATION_SIXTY_MOVES",
  "TERMINATION_STALEMATE",
  "Board",
  "parse_square",
  "piece_name",
  "piece_symbol",
  "square",
  "square_distance",
  "square_file",
  "square_manhattan_distance",
  "square_mirror",
  "square_name",
  "square_rank",
]
