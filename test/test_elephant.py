import pytest
from libxiangqi import Board, IllegalMove


def test_red_elephant_move_diagonal():
    """Test red elephant can move two steps diagonally"""
    g = Board()
    # Move soldier
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    # Move elephant diagonally
    g.make_move(2, 0, 4, 2)


def test_black_elephant_move_diagonal():
    """Test black elephant can move two steps diagonally"""
    g = Board()
    # Red move
    g.make_move(4, 3, 4, 4)

    # Black elephant moves diagonally
    g.make_move(2, 9, 4, 7)


def test_elephant_blocked_by_piece():
    """Test elephant cannot jump over pieces (elephant eye blocked)"""
    g = Board()
    # Move cannon to (1,1) to block the elephant eye for (2,0) -> (0,2)
    g.make_move(1, 2, 1, 1)
    g.make_move(4, 6, 4, 5)

    # Elephant at (2,0) cannot jump to (0,2) because the eye (1,1) is blocked
    with pytest.raises(IllegalMove):
        g.make_move(2, 0, 0, 2)


def test_red_elephant_cannot_cross_river():
    """Test red elephant cannot cross the river (rank > 4)"""
    g = Board()
    # Move soldier
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    # Move elephant to edge of river
    g.make_move(2, 0, 4, 2)
    g.make_move(0, 6, 0, 5)
    g.make_move(4, 2, 2, 4)
    g.make_move(0, 5, 0, 4)

    # Try to cross river
    with pytest.raises(IllegalMove):
        g.make_move(2, 4, 4, 6)


def test_black_elephant_cannot_cross_river():
    """Test black elephant cannot cross the river (rank < 5)"""
    g = Board()
    # Red move
    g.make_move(4, 3, 4, 4)

    # Black elephant to edge of river
    g.make_move(2, 9, 4, 7)
    g.make_move(0, 3, 0, 4)
    g.make_move(4, 7, 2, 5)
    g.make_move(0, 4, 0, 5)

    # Try to cross river
    with pytest.raises(IllegalMove):
        g.make_move(2, 5, 4, 3)


def test_elephant_cannot_move_one_step():
    """Test elephant must move exactly 2 diagonal steps"""
    g = Board()
    # Move soldier
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    # Try to move elephant one step
    with pytest.raises(IllegalMove):
        g.make_move(2, 0, 3, 1)


def test_elephant_cannot_move_orthogonally():
    """Test elephant cannot move in straight lines"""
    g = Board()
    # Move soldier
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    # Try to move elephant orthogonally
    with pytest.raises(IllegalMove):
        g.make_move(2, 0, 2, 2)
