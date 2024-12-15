import unittest
import camelup
import copy


class EndOfRoundTest(unittest.TestCase):

    def setUp(self):
        self.g = camelup.GameState()

    def test_end_of_round_scoring_only_rolls(self):
        expected_money = copy.deepcopy(self.g.player_money_values)

        camelup.move_camel(g=self.g, player=0)
        camelup.move_camel(g=self.g, player=1)
        camelup.move_camel(g=self.g, player=2)
        camelup.move_camel(g=self.g, player=3)
        camelup.move_camel(g=self.g, player=0)
        expected_money[0] += 2
        expected_money[1] += 1
        expected_money[2] += 1
        expected_money[3] += 1
        self.assertEqual(expected_money, self.g.player_money_values)

    def test_end_of_round_scoring_with_bets(self):
        # Remove camels from start positions
        self.g.camel_track[0] = []
        self.g.camel_track[1] = []
        self.g.camel_track[2] = []

        self.g.camel_yet_to_move = [True, False, False, False, False]
        self.g.camel_track[0] = ["c_0"]
        self.g.camel_track[8] = ["c_1", "c_2"]
        self.g.camel_track[10] = ["c_4"]
        self.g.camel_track[12] = ["c_3"]

        self.g.round_bets = [
            ["c_3", 0], ["c_3", 1], ["c_2", 3],
            ["c_3", 1], ["c_4", 2], ["c_0", 3]]

        expected_coins = copy.deepcopy(self.g.player_money_values)
        camelup.move_camel(g=self.g, player=0)

        expected_coins[0] += 1  # Coin for rolling
        expected_coins[0] += self.g.FIRST_PLACE_ROUND_PAYOUT[0]  # Payout for first to choose first
        expected_coins[1] += self.g.FIRST_PLACE_ROUND_PAYOUT[1]  # Payout for second to choose first
        expected_coins[3] += self.g.THIRD_OR_WORSE_PLACE_ROUND_PAYOUT  # Payout for third or worse bet
        expected_coins[1] += self.g.FIRST_PLACE_ROUND_PAYOUT[2]  # Payout for third to choose first
        expected_coins[2] += self.g.SECOND_PLACE_ROUND_PAYOUT[0]  # Payout for first to choose second
        expected_coins[3] += self.g.THIRD_OR_WORSE_PLACE_ROUND_PAYOUT  # Payout for third or worse bet

        self.assertEqual(expected_coins, self.g.player_money_values)


if __name__ == '__main__':
    unittest.main()
