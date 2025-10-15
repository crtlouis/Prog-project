import unittest
from connect_four import new_board, place_piece, winning_cells, is_full

class TestConnectFourLogic(unittest.TestCase):
    """Unit tests for core game functions."""

    def test_new_board(self):
        board = new_board()
        self.assertEqual(len(board), 6)
        self.assertEqual(len(board[0]), 7)
        self.assertTrue(all(cell == 0 for row in board for cell in row))

    def test_vertical_win(self):
        board = new_board()
        for i in range(4):
            place_piece(board, i, 0, 1)
        self.assertIsNotNone(winning_cells(board, 1))

    def test_horizontal_win(self):
        board = new_board()
        for c in range(4):
            place_piece(board, 0, c, 2)
        self.assertIsNotNone(winning_cells(board, 2))

    def test_full_board(self):
        board = [[1]*7 for _ in range(6)]
        self.assertTrue(is_full(board))

if __name__ == "__main__":
    unittest.main()
