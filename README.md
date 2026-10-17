# libxiangqi: a Xiangqi library for Python
## Under heavy development

libxiangqi is a python-chess like library for the game xiangqi

https://en.wikipedia.org/wiki/Xiangqi

Pure Python, no compilation required.

## Quick Start

```python
from libxiangqi import Board

b = Board()
b.serve()  # Start web interface at http://127.0.0.1:9999
```

## Usage

The API mirrors [python-chess](https://python-chess.readthedocs.io/) where
possible. Squares are `a1`..`i10` (files a-i, ranks 1-10), red moves first.

```python
from libxiangqi import Board, Move, Piece, RED, BLACK, GENERAL, parse_square

b = Board()

# Make moves (UCI-style notation)
b.push_uci("e4e5")          # red soldier e4 -> e5
b.push_uci("e7e6")          # black soldier e7 -> e6

# Or with Move objects
move = Move.from_uci("h2e2")  # red cannon h2 -> e2
b.push(move)

# Inspect the position
b.turn                       # RED or BLACK
b.fen()                      # FEN string
b.legal_moves                # generator of legal moves
b.piece_at(parse_square("e1"))  # Piece or None
b.is_check()                 # is the side to move in check?
b.is_checkmate()
b.is_game_over()

# Undo moves
b.pop()                      # unmake the last move

# Set up a position from FEN
b2 = Board("rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1")
```

## Development

```bash
uv sync
uv run pytest
uv run ruff check libxiangqi/ test/
uv run mypy libxiangqi/
```
