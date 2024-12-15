import unittest
import camelup


class GameBetTest(unittest.TestCase):

    def setUp(self):
        self.g = camelup.GameState()

        # Remove camels from start positions
        self.g.camel_track[0] = []
        self.g.camel_track[1] = []
        self.g.camel_track[2] = []

    def test_make_new_bet(self):
        camelup.place_game_bet(g=self.g, camel="c_1", player=1, bet_type="win")
        expected_winner_bets = [["c_1", 1]]
        expected_loser_bets = []
        self.assertEqual(self.g.game_winner_bets, expected_winner_bets)
        self.assertEqual(self.g.game_loser_bets, expected_loser_bets)

    def test_make_duplicate_bet_on_same_stack(self):
        camelup.place_game_bet(g=self.g, camel="c_1", player=1, bet_type="win")
        camelup.place_game_bet(g=self.g, camel="c_1", player=2, bet_type="win")
        camelup.place_game_bet(g=self.g, camel="c_2", player=2, bet_type="win")
        self.assertRaises(ValueError, camelup.place_game_bet, g=self.g, camel="c_1", player=1, bet_type="win")
        expected_winner_bets = [["c_1", 1], ["c_1", 2], ["c_2", 2]]
        expected_loser_bets = []
        self.assertEqual(self.g.game_winner_bets, expected_winner_bets)
        self.assertEqual(self.g.game_loser_bets, expected_loser_bets)

    def test_make_duplicate_bet_on_different_stacks(self):
        camelup.place_game_bet(g=self.g, camel="c_1", player=1, bet_type="win")
        camelup.place_game_bet(g=self.g, camel="c_1", player=2, bet_type="lose")
        self.assertRaises(ValueError, camelup.place_game_bet, g=self.g, camel="c_1", player=1, bet_type="lose")
        expected_winner_bets = [["c_1", 1]]
        expected_loser_bets = [["c_1", 2]]
        self.assertEqual(self.g.game_winner_bets, expected_winner_bets)
        self.assertEqual(self.g.game_loser_bets, expected_loser_bets)

    def test_make_invalid_bet_type(self):
        self.assertRaises(ValueError, camelup.place_game_bet, g=self.g, camel="c_1", player=1, bet_type="notabet")


if __name__ == '__main__':
    unittest.main()
