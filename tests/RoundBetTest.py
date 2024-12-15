import unittest
import camelup


class RoundBetTest(unittest.TestCase):

    def setUp(self):
        self.g = camelup.GameState()

        # Remove camels from start positions
        self.g.camel_track[0] = []
        self.g.camel_track[1] = []
        self.g.camel_track[2] = []

    def test_make_new_bet(self):
        camelup.place_round_winner_bet(g=self.g, camel="c_2", player=3)
        camelup.place_round_winner_bet(g=self.g, camel="c_1", player=1)
        camelup.place_round_winner_bet(g=self.g, camel="c_1", player=2)
        expected_round_bets = [["c_2", 3], ["c_1", 1], ["c_1", 2]]
        self.assertEqual(expected_round_bets, self.g.round_bets)

    def test_make_too_many_bets(self):
        camelup.place_round_winner_bet(g=self.g, camel="c_1", player=3)
        camelup.place_round_winner_bet(g=self.g, camel="c_1", player=1)
        camelup.place_round_winner_bet(g=self.g, camel="c_1", player=2)
        self.assertRaises(ValueError, camelup.place_round_winner_bet, g=self.g, camel="c_1", player=3)
        expected_round_bets = [["c_1", 3], ["c_1", 1], ["c_1", 2]]
        self.assertEqual(expected_round_bets, self.g.round_bets)


if __name__ == '__main__':
    unittest.main()
