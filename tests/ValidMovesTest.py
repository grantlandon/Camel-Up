import unittest
from camelup import *


class ValidMovesTest(unittest.TestCase):

    def setUp(self):
        self.g = GameState()

        # Set up camels
        self.g.camel_track[0] = []
        self.g.camel_track[1] = ["c_2"]
        self.g.camel_track[2] = []
        self.g.camel_track[3] = ["c_1", "c_3"]
        self.g.camel_track[5] = ["c_4"]
        self.g.camel_track[8] = ["c_0"]

        # Set up traps
        self.g.trap_track[2] = [1, 2]
        self.g.trap_track[4] = [-1, 0]
        self.g.trap_track[6] = [-1, 3]
        self.g.trap_track[9] = [1, 1]

        # Set up round bets
        self.g.round_bets = [
            ["c_1", 0], ["c_1", 1],
            ["c_0", 3], ["c_0", 0], ["c_0", 2],
            ["c_2", 1], ["c_2", 2]]

        # Set up game bets
        # Note: The valid moves engine doesn't actually check the order of bets as that is end-game logic. This test
        # only validates the player bets. The function for placing game bets must ensure that the lists are
        # consistent
        self.g.game_winner_bets = [['c_1', 0], ['c_4', 1], ['c_1', 3], ['c_0', 3], ['c_2', 2]]
        self.g.game_loser_bets = [['c_4', 0], ['c_2', 1], ["c_1", 1], ["c_3", 1], ["c_0", 1]]

    def test_valid_moves(self):
        valid_moves_0 = get_valid_moves(self.g, 0)
        valid_moves_1 = get_valid_moves(self.g, 1)
        valid_moves_2 = get_valid_moves(self.g, 2)
        valid_moves_3 = get_valid_moves(self.g, 3)

        expected_result_0 = {
            (0,),
            (1, 1, 11),
            (1, 1, 12),
            (1, 1, 13),
            (1, 1, 14),
            (1, 1, 15),
            (1, -1, 11),
            (1, -1, 12),
            (1, -1, 13),
            (1, -1, 14),
            (1, -1, 15),
            (2, "c_1"),
            (2, "c_2"),
            (2, "c_3"),
            (2, "c_4"),
            (3, "win", "c_0"),
            (3, "win", "c_2"),
            (3, "win", "c_3"),
            (3, "lose", "c_0"),
            (3, "lose", "c_2"),
            (3, "lose", "c_3")}

        expected_result_1 = {
            (0,),
            (1, 1, 10),
            (1, 1, 11),
            (1, 1, 12),
            (1, 1, 13),
            (1, 1, 14),
            (1, 1, 15),
            (1, -1, 10),
            (1, -1, 11),
            (1, -1, 12),
            (1, -1, 13),
            (1, -1, 14),
            (1, -1, 15),
            (2, "c_1"),
            (2, "c_2"),
            (2, "c_3"),
            (2, "c_4")}

        expected_result_2 = {
            (0,),
            (1, 1, 11),
            (1, 1, 12),
            (1, 1, 13),
            (1, 1, 14),
            (1, 1, 15),
            (1, -1, 11),
            (1, -1, 12),
            (1, -1, 13),
            (1, -1, 14),
            (1, -1, 15),
            (2, "c_1"),
            (2, "c_2"),
            (2, "c_3"),
            (2, "c_4"),
            (3, "win", "c_0"),
            (3, "win", "c_1"),
            (3, "win", "c_3"),
            (3, "win", "c_4"),
            (3, "lose", "c_0"),
            (3, "lose", "c_1"),
            (3, "lose", "c_3"),
            (3, "lose", "c_4")}

        expected_result_3 = {
            (0,),
            (1, 1, 7),
            (1, 1, 11),
            (1, 1, 12),
            (1, 1, 13),
            (1, 1, 14),
            (1, 1, 15),
            (1, -1, 7),
            (1, -1, 11),
            (1, -1, 12),
            (1, -1, 13),
            (1, -1, 14),
            (1, -1, 15),
            (2, "c_1"),
            (2, "c_2"),
            (2, "c_3"),
            (2, "c_4"),
            (3, "win", "c_2"),
            (3, "win", "c_3"),
            (3, "win", "c_4"),
            (3, "lose", "c_2"),
            (3, "lose", "c_3"),
            (3, "lose", "c_4")}

        self.assertEqual(set(valid_moves_0), set(expected_result_0))
        self.assertEqual(set(valid_moves_1), set(expected_result_1))
        self.assertEqual(set(valid_moves_2), set(expected_result_2))
        self.assertEqual(set(valid_moves_3), set(expected_result_3))


if __name__ == '__main__':
    unittest.main()
