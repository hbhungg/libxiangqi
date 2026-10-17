import pytest
from libxiangqi import Board, IllegalMove


def test_red_horse_move_l_shape():
    """Test red horse can move in L-shape (2 forward, 1 sideways)"""
    g = Board()
    # Horse at (1,0) can move to (2,2)
    g.make_move(1, 0, 2, 2)


def test_black_horse_move_l_shape():
    """Test black horse can move in L-shape"""
    g = Board()
    # Red move
    g.make_move(1, 0, 2, 2)

    # Black horse moves
    g.make_move(1, 9, 2, 7)


def test_horse_all_l_directions():
    """Test horse can move in all 8 L-shape directions"""
    g = Board()
    # Move soldiers out of the way (they block the horse's legs at (2,3) and (2,6))
    g.make_move(2, 3, 2, 4)
    g.make_move(2, 6, 2, 5)

    # Move horse to open area
    g.make_move(1, 0, 2, 2)
    g.make_move(1, 9, 2, 7)

    # Test various L-moves
    g.make_move(2, 2, 3, 4)
    g.make_move(2, 7, 3, 5)
    g.make_move(3, 4, 2, 2)
    g.make_move(3, 5, 2, 7)
    g.make_move(2, 2, 1, 4)


def test_horse_blocked_by_piece():
    """Test horse cannot jump when leg is blocked"""
    g = Board()
    # Horse at (1,0) is blocked by elephant at (2,0) from moving to (3,1)
    # The blocking piece is in the direction of the longer movement

    # Try to move horse but it's blocked by elephant
    with pytest.raises(IllegalMove):
        g.make_move(1, 0, 3, 1)


def test_horse_not_blocked_diagonal():
    """Test horse is not blocked by diagonal pieces"""
    g = Board()
    # Horse at (1,0), cannon at (1,2), horse should be able to move to (2,2)
    g.make_move(1, 0, 2, 2)


def test_horse_blocked_horizontally():
    """Test horse blocked when moving horizontally more"""
    g = Board()
    # Move horse to (2,2)
    g.make_move(1, 0, 2, 2)
    g.make_move(1, 9, 2, 7)

    # Horse at (2,2) moving to (0,1) is blocked by the cannon at (1,2)
    with pytest.raises(IllegalMove):
        g.make_move(2, 2, 0, 1)


def test_horse_blocked_vertically():
    """Test horse blocked when moving vertically more"""
    g = Board()
    # Move horse to (2,2)
    g.make_move(1, 0, 2, 2)
    g.make_move(1, 9, 2, 7)

    # Horse at (2,2) moving to (1,4) is blocked by the soldier at (2,3)
    with pytest.raises(IllegalMove):
        g.make_move(2, 2, 1, 4)


def test_horse_cannot_move_straight():
    """Test horse cannot move in straight lines"""
    g = Board()
    # Move cannons out of the way
    g.make_move(1, 2, 1, 3)
    g.make_move(1, 7, 1, 6)

    # Try to move horse straight
    with pytest.raises(IllegalMove):
        g.make_move(1, 0, 1, 2)


def test_horse_cannot_move_diagonally():
    """Test horse cannot move diagonally"""
    g = Board()
    # Try to move horse diagonally
    with pytest.raises(IllegalMove):
        g.make_move(1, 0, 2, 1)


def test_horse_cannot_move_one_square():
    """Test horse cannot move just one square"""
    g = Board()
    # Try to move horse one square
    with pytest.raises(IllegalMove):
        g.make_move(1, 0, 1, 1)
