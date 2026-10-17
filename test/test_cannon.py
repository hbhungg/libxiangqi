import pytest
from libxiangqi import Board, IllegalMove


def test_red_cannon_move_without_jump():
    """Test cannon can move without jumping when not capturing"""
    g = Board()
    # Cannon at (1,2) can move to (1,4) if path is clear
    # First move soldier out of way
    g.make_move(0, 3, 0, 4)
    g.make_move(0, 6, 0, 5)

    # Now move cannon
    g.make_move(1, 2, 1, 4)


def test_black_cannon_move_without_jump():
    """Test black cannon can move without jumping"""
    g = Board()
    # Red move
    g.make_move(0, 3, 0, 4)

    # Black cannon moves
    g.make_move(1, 7, 1, 5)


def test_cannon_move_horizontally():
    """Test cannon can move horizontally"""
    g = Board()
    # Move soldier
    g.make_move(0, 3, 0, 4)
    g.make_move(0, 6, 0, 5)

    # Move cannon horizontally
    g.make_move(1, 2, 0, 2)


def test_cannon_capture_with_screen():
    """Test cannon must jump over exactly one piece to capture"""
    g = Board()
    # Move pieces to set up a capture
    # Cannon at (1,2), soldier at (4,3), want to capture black soldier at (4,6)
    g.make_move(1, 2, 4, 2)
    g.make_move(0, 6, 0, 5)

    # Now cannon at (4,2), there's a red soldier at (4,3), and black soldier at (4,6)
    # Cannon should be able to capture the black soldier
    g.make_move(4, 2, 4, 6)


def test_cannon_cannot_capture_without_screen():
    """Test cannon cannot capture without a screen piece"""
    g = Board()
    # Move cannon
    g.make_move(1, 2, 1, 4)
    g.make_move(1, 7, 1, 5)

    # Try to capture without screen
    with pytest.raises(IllegalMove):
        g.make_move(1, 4, 1, 5)


def test_cannon_cannot_move_with_blocking_piece():
    """Test cannon cannot move through pieces when not capturing"""
    g = Board()
    # Move horse to (2,2) to block the cannon's horizontal path
    g.make_move(1, 0, 2, 2)
    g.make_move(4, 6, 4, 5)

    # Cannon at (1,2) cannot move to (3,2) because horse at (2,2) blocks the path
    with pytest.raises(IllegalMove):
        g.make_move(1, 2, 3, 2)


def test_cannon_cannot_capture_with_two_screens():
    """Test cannon cannot capture if there are 2+ pieces in between"""
    g = Board()
    # Set up: cannon at (4,2), red soldier at (4,3), black soldier at (4,4), black soldier at (4,6)
    g.make_move(1, 2, 4, 2)
    g.make_move(4, 6, 4, 5)
    g.make_move(0, 3, 0, 4)
    g.make_move(4, 5, 4, 4)
    g.make_move(0, 4, 0, 5)
    g.make_move(2, 6, 2, 5)

    # Cannon at (4,2) trying to capture at (4,6) has 2 screens (4,3) and (4,4) - should fail
    with pytest.raises(IllegalMove):
        g.make_move(4, 2, 4, 6)


def test_cannon_cannot_move_diagonally():
    """Test cannon can only move in straight lines"""
    g = Board()
    # Try to move cannon diagonally
    with pytest.raises(IllegalMove):
        g.make_move(1, 2, 2, 3)


def test_cannon_horizontal_capture():
    """Test cannon can capture horizontally with a screen"""
    g = Board()
    # Move cannon to (3,4)
    g.make_move(1, 2, 1, 4)
    g.make_move(6, 6, 6, 5)
    g.make_move(1, 4, 3, 4)
    g.make_move(6, 5, 6, 4)

    # Move soldier to (4,4) to be the screen
    g.make_move(4, 3, 4, 4)
    g.make_move(6, 4, 5, 4)

    # Now capture black soldier at (5,4) with screen at (4,4)
    g.make_move(3, 4, 5, 4)


def test_cannon_cannot_jump_to_empty():
    """Test cannon cannot jump over piece to move to empty square"""
    g = Board()
    # Move black cannon to (1,3) to be the screen
    g.make_move(0, 3, 0, 4)
    g.make_move(1, 7, 1, 5)
    g.make_move(0, 4, 0, 5)
    g.make_move(1, 5, 1, 3)

    # Try to jump over black cannon at (1,3) to empty square (1,4)
    with pytest.raises(IllegalMove):
        g.make_move(1, 2, 1, 4)
