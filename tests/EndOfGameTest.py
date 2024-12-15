import unittest
import camelup
import copy


class EndOfRoundTest(unittest.TestCase):

    def setUp(self):
        self.g = camelup.GameState()

        # Remove camels from start positions
        self.g.camel_track[0] = []
        self.g.camel_track[1] = []
        self.g.camel_track[2] = []

    def test_end_of_round_scoring(self):
        expected_coins = copy.deepcopy(self.g.player_money_values)

        self.g.camel_yet_to_move = [True, False, False, False, False]
        self.g.camel_track[15] = ["c_0"]
        self.g.camel_track[8] = ["c_1", "c_2"]
        self.g.camel_track[10] = ["c_4"]
        self.g.camel_track[12] = ["c_3"]

        self.g.game_winner_bets = [
            ["c_0", 0], ["c_0", 1], ["c_2", 3],
            ["c_3", 2], ["c_4", 2], ["c_0", 2],
            ["c_0", 3]]

        self.g.game_loser_bets = [
            ["c_1", 1], ["c_1", 2], ["c_3", 0],
            ["c_4", 3], ["c_0", 3], ["c_1", 3],
            ["c_1", 0]]

        camelup.move_camel(g=self.g, player=0)

        expected_coins[0] += 1  # Coin for rolling

        expected_coins[0] += self.g.get_game_bets_payout(0)  # Payout for first to choose winner
        expected_coins[1] += self.g.get_game_bets_payout(1)  # Payout for second to choose winner
        expected_coins[3] += self.g.BAD_GAME_END_BET  # Payout for bad bet on winner
        expected_coins[2] += self.g.BAD_GAME_END_BET  # Payout for bad bet on winner
        expected_coins[2] += self.g.BAD_GAME_END_BET  # Payout for bad bet on winner
        expected_coins[2] += self.g.get_game_bets_payout(2)  # Payout for third to choose winner
        expected_coins[3] += self.g.get_game_bets_payout(3)  # Payout for fourth to choose winner

        expected_coins[1] += self.g.get_game_bets_payout(0)  # Payout for first to choose loser
        expected_coins[2] += self.g.get_game_bets_payout(1)  # Payout for second to choose loser
        expected_coins[0] += self.g.BAD_GAME_END_BET  # Payout for bad bet on loser
        expected_coins[3] += self.g.BAD_GAME_END_BET  # Payout for bad bet on loser
        expected_coins[3] += self.g.BAD_GAME_END_BET  # Payout for bad bet on loser
        expected_coins[3] += self.g.get_game_bets_payout(2)  # Payout for third to choose loser
        expected_coins[0] += self.g.get_game_bets_payout(3)  # Payout for fourth to choose loser

        self.assertEqual(expected_coins, self.g.player_money_values)


if __name__ == '__main__':
    unittest.main()
