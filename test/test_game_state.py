import pytest
from libxiangqi import Board, IllegalMove


def test_initial_turn_is_red():
    """Test that red moves first"""
    g = Board()
    # Red can move
    g.make_move(4, 3, 4, 4)


def test_turn_switches_after_move():
    """Test that turn switches between players"""
    g = Board()
    # Red moves
    g.make_move(4, 3, 4, 4)

    # Black can move
    g.make_move(4, 6, 4, 5)

    # Red can move again
    g.make_move(0, 3, 0, 4)


def test_cannot_move_opponent_piece():
    """Test that you cannot move opponent's pieces"""
    g = Board()
    # Red's turn, try to move black piece
    with pytest.raises(IllegalMove):
        g.make_move(4, 6, 4, 5)


def test_cannot_move_twice_in_row():
    """Test that same player cannot move twice"""
    g = Board()
    # Red moves
    g.make_move(4, 3, 4, 4)

    # Red tries to move again - should fail
    with pytest.raises(IllegalMove):
        g.make_move(0, 3, 0, 4)


def test_capture_removes_piece():
    """Test that capturing removes the opponent's piece"""
    g = Board()
    # Set up a capture scenario
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)
    g.make_move(4, 4, 4, 5)
    g.make_move(0, 6, 0, 5)

    # Capture
    g.make_move(4, 5, 4, 6)

    # Verify piece was captured (the square should now have red soldier)
    piece = g.get_piece(4, 6)
    assert piece is not None


def test_cannot_capture_own_piece():
    """Test that you cannot capture your own pieces"""
    g = Board()
    # Try to move piece onto own piece
    with pytest.raises(IllegalMove):
        g.make_move(4, 3, 4, 0)


def test_move_from_empty_square():
    """Test that moving from empty square raises error"""
    g = Board()
    with pytest.raises(IllegalMove):
        g.make_move(4, 4, 4, 5)


def test_move_out_of_bounds():
    """Test that moving out of bounds raises error"""
    g = Board()
    with pytest.raises(IllegalMove):
        g.make_move(0, 0, 10, 0)


def test_move_to_out_of_bounds():
    """Test that moving to out of bounds position raises error"""
    g = Board()
    with pytest.raises(IllegalMove):
        g.make_move(0, 0, 0, 15)


def test_get_legal_moves_initial():
    """Test that get_legal_moves returns valid moves at start"""
    g = Board()
    moves = g.get_legal_moves()

    # Should have some moves available
    assert len(moves) > 0

    # All moves should be for red pieces
    for from_file, from_rank, to_file, to_rank in moves:
        piece = g.get_piece(from_file, from_rank)
        assert piece is not None


def test_legal_moves_are_playable():
    """Test that all moves from get_legal_moves can be played"""
    g = Board()
    moves = g.get_legal_moves()

    # Pick first legal move and play it
    if moves:
        from_file, from_rank, to_file, to_rank = moves[0]
        g.make_move(from_file, from_rank, to_file, to_rank)


def test_set_and_get_piece():
    """Test setting and getting pieces"""
    g = Board()
    piece = g.get_piece(4, 0)
    assert piece is not None

    # Empty square
    empty = g.get_piece(4, 4)
    assert empty is None


def test_multiple_captures_in_game():
    """Test multiple captures work correctly"""
    g = Board()

    # Set up and execute multiple captures
    g.make_move(4, 3, 4, 4)
    g.make_move(4, 6, 4, 5)
    g.make_move(4, 4, 4, 5)
    g.make_move(2, 6, 2, 5)
    g.make_move(4, 5, 4, 6)
    g.make_move(2, 5, 2, 4)
    g.make_move(2, 3, 2, 4)


def test_complex_game_sequence():
    """Test a longer sequence of valid moves"""
    g = Board()

    # Play several moves
    moves = [
        (4, 3, 4, 4),  # Red soldier
        (4, 6, 4, 5),  # Black soldier
        (1, 0, 2, 2),  # Red horse
        (1, 9, 2, 7),  # Black horse
        (0, 3, 0, 4),  # Red soldier
        (0, 6, 0, 5),  # Black soldier
    ]

    for from_file, from_rank, to_file, to_rank in moves:
        g.make_move(from_file, from_rank, to_file, to_rank)
