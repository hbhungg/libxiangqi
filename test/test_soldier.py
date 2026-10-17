import pytest
from libxiangqi import Board, IllegalMove


def test_red_soldier_move():
    """Test red soldier can move forward"""
    g = Board()
    g.make_move(4, 3, 4, 4)


def test_black_soldier_move():
    """Test black soldier can move forward"""
    g = Board()
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)


def test_red_soldier_no_move_sideway_before_river():
    """Test red soldier cannot move sideways before crossing river"""
    g = Board()
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)
    with pytest.raises(IllegalMove):
        g.make_move(2, 3, 3, 3)


def test_black_soldier_no_move_sideway_before_river():
    """Test black soldier cannot move sideways before crossing river"""
    g = Board()
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)
    g.make_move(0, 3, 0, 4)

    with pytest.raises(IllegalMove):
        g.make_move(2, 6, 3, 6)


def test_red_soldier_move_sideway_after_river():
    """Test red soldier can move sideways after crossing river"""
    g = Board()
    # Move soldier across river on file 2 (file 4 would expose the flying general)
    g.make_move(2, 3, 2, 4)
    g.make_move(2, 6, 2, 5)
    g.make_move(2, 4, 2, 5)
    g.make_move(0, 6, 0, 5)

    # Now soldier can move sideways
    g.make_move(2, 5, 1, 5)


def test_black_soldier_move_sideway_after_river():
    """Test black soldier can move sideways after crossing river"""
    g = Board()
    # Move black soldier across river on file 2 (file 4 would expose the flying general)
    g.make_move(2, 3, 2, 4)
    g.make_move(2, 6, 2, 5)
    g.make_move(0, 3, 0, 4)
    g.make_move(2, 5, 2, 4)
    g.make_move(0, 4, 0, 5)

    # Black soldier can now move sideways
    g.make_move(2, 4, 1, 4)


def test_red_soldier_cannot_move_backward():
    """Test red soldier cannot move backward"""
    g = Board()
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    with pytest.raises(IllegalMove):
        g.make_move(4, 4, 4, 3)


def test_black_soldier_cannot_move_backward():
    """Test black soldier cannot move backward"""
    g = Board()
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    with pytest.raises(IllegalMove):
        g.make_move(4, 5, 4, 6)


def test_soldier_cannot_move_diagonally():
    """Test soldier cannot move diagonally"""
    g = Board()
    with pytest.raises(IllegalMove):
        g.make_move(4, 3, 5, 4)


def test_soldier_cannot_move_two_steps():
    """Test soldier can only move one step at a time"""
    g = Board()
    with pytest.raises(IllegalMove):
        g.make_move(4, 3, 4, 5)


def test_red_soldier_forward_always_allowed():
    """Test red soldier can always move forward regardless of river"""
    g = Board()
    # Before river
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    # After crossing river
    g.make_move(4, 4, 4, 5)
    g.make_move(0, 6, 0, 5)
    g.make_move(4, 5, 4, 6)


def test_black_soldier_forward_always_allowed():
    """Test black soldier can always move forward regardless of river"""
    g = Board()
    # Before river
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)

    # After crossing river
    g.make_move(0, 3, 0, 4)
    g.make_move(4, 5, 4, 4)
    g.make_move(0, 4, 0, 5)
    g.make_move(4, 4, 4, 3)


def test_soldier_capture():
    """Test soldier can capture enemy pieces"""
    g = Board()
    # Move soldiers toward each other
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)
    g.make_move(4, 4, 4, 5)
    g.make_move(0, 6, 0, 5)

    # Red soldier captures black soldier
    g.make_move(4, 5, 4, 6)


def test_soldier_sideways_capture_after_river():
    """Test soldier can capture sideways after crossing river"""
    g = Board()
    # Get red soldier across river
    g.make_move(4, 3, 4, 4)
    g.make_move(1, 7, 1, 5)
    g.make_move(4, 4, 4, 5)
    g.make_move(1, 5, 3, 5)

    # Soldier captures black cannon sideways
    g.make_move(4, 5, 3, 5)


def test_red_soldier_at_river_boundary():
    """Test red soldier at rank 4 (river boundary) can still only move forward"""
    g = Board()
    # Move to rank 4
    g.make_move(4, 3, 4, 4)
    g.make_move(0, 6, 0, 5)

    # At rank 4, cannot move sideways yet
    with pytest.raises(IllegalMove):
        g.make_move(4, 4, 5, 4)


def test_black_soldier_at_river_boundary():
    """Test black soldier at rank 5 (river boundary) can still only move forward"""
    g = Board()
    # Move to rank 5
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)
    g.make_move(0, 3, 0, 4)

    # At rank 5, cannot move sideways yet
    with pytest.raises(IllegalMove):
        g.make_move(4, 5, 5, 5)


def test_red_soldier_just_crossed_river():
    """Test red soldier at rank 5 (just crossed) can move sideways"""
    g = Board()
    # Cross river to rank 5 on file 2 (file 4 would expose the flying general)
    g.make_move(2, 3, 2, 4)
    g.make_move(2, 6, 2, 5)
    g.make_move(2, 4, 2, 5)
    g.make_move(0, 6, 0, 5)

    # Can now move sideways
    g.make_move(2, 5, 1, 5)


def test_black_soldier_just_crossed_river():
    """Test black soldier at rank 4 (just crossed) can move sideways"""
    g = Board()
    # Cross river to rank 4 on file 2 (file 4 would expose the flying general)
    g.make_move(2, 3, 2, 4)
    g.make_move(2, 6, 2, 5)
    g.make_move(0, 3, 0, 4)
    g.make_move(2, 5, 2, 4)
    g.make_move(0, 4, 0, 5)

    # Can now move sideways
    g.make_move(2, 4, 1, 4)


def test_soldier_cannot_move_sideways_both_directions_at_once():
    """Test soldier can only move one direction at a time"""
    g = Board()
    # Cross river on file 2 (file 4 would expose the flying general)
    g.make_move(2, 3, 2, 4)
    g.make_move(2, 6, 2, 5)
    g.make_move(2, 4, 2, 5)
    g.make_move(0, 6, 0, 5)

    # Move sideways left
    g.make_move(2, 5, 1, 5)
    g.make_move(0, 5, 0, 4)

    # Can move sideways right from new position
    g.make_move(1, 5, 2, 5)
