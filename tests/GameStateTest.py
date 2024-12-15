import unittest
import camelup
import copy


class EndOfRoundTest(unittest.TestCase):

    def setUp(self):
        self.g = camelup.GameState()

    def test_player_copy(self):
        self.g.game_winner_bets = [["c_2", 1], ["c_3", 0], ["c_4", 0], ["c_4", 3]]
        self.g.game_loser_bets = [["c_2", 0], ["c_3", 0]]
        player_copy = self.g.get_player_copy(player=0)
        expected_gwb = [[None, None], ["c_3", 0], ["c_4", 0], [None, None]]
        expected_glb = [["c_2", 0], ["c_3", 0]]
        self.assertEqual(expected_gwb, player_copy.game_winner_bets)
        self.assertEqual(expected_glb, player_copy.game_loser_bets)


if __name__ == '__main__':
    unittest.main()
