import pytest
from libxiangqi import Board, IllegalMove


def test_red_general_move_forward():
    """Test red general can move forward one step within palace"""
    g = Board()
    # Move soldier out of the way
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    # Move general forward
    g.make_move(4, 0, 4, 1)


def test_red_general_move_sideways():
    """Test red general can move sideways within palace"""
    g = Board()
    # Move soldier
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    # Move advisor out of the way, then move general sideways
    g.make_move(3, 0, 4, 1)
    g.make_move(0, 6, 0, 5)
    g.make_move(4, 0, 3, 0)


def test_black_general_move():
    """Test black general can move within palace"""
    g = Board()
    # Red move
    g.make_move(4, 3, 4, 4)

    # Black general moves forward
    g.make_move(4, 9, 4, 8)


def test_general_cannot_leave_palace_horizontal():
    """Test general cannot move outside palace horizontally"""
    g = Board()
    # Move soldier
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    # Try to move general outside palace (file must be 3-5)
    with pytest.raises(IllegalMove):
        g.make_move(4, 0, 2, 0)


def test_general_cannot_leave_palace_vertical():
    """Test red general cannot move outside palace vertically (rank > 2)"""
    g = Board()
    # Move soldier
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    # Move general to edge of palace
    g.make_move(4, 0, 4, 1)
    g.make_move(0, 6, 0, 5)
    g.make_move(4, 1, 4, 2)
    g.make_move(0, 5, 0, 4)

    # Try to move general outside palace
    with pytest.raises(IllegalMove):
        g.make_move(4, 2, 4, 3)


def test_general_cannot_move_diagonally():
    """Test general cannot move diagonally"""
    g = Board()
    # Move soldier
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    # Try to move general diagonally
    with pytest.raises(IllegalMove):
        g.make_move(4, 0, 3, 1)


def test_general_cannot_move_two_steps():
    """Test general cannot move more than one step"""
    g = Board()
    # Move soldier
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    # Try to move general two steps
    with pytest.raises(IllegalMove):
        g.make_move(4, 0, 4, 2)
