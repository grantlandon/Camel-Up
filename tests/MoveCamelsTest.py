import unittest
import unittest.mock
import copy
import camelup


class MoveCamelsTest(unittest.TestCase):

    def setUp(self):
        self.g = camelup.GameState()

        # Remove camels from start positions
        self.g.camel_track[0] = []
        self.g.camel_track[1] = []
        self.g.camel_track[2] = []

    def test_move_one_camel_to_empty(self):
        self.g.camel_track[10] = ["c_1", "c_2", "c_3", "c_4"]
        self.g.camel_track[12] = ["c_0"]

        def mock_random_camel(_):
            return 0

        def mock_roll(move_range):
            return 2

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 0)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[10] = ["c_1", "c_2", "c_3", "c_4"]
                expected_track[14] = ["c_0"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

    def test_move_stacked_camel_to_empty(self):
        self.g.camel_track[10] = ["c_1", "c_2", "c_3", "c_4"]
        self.g.camel_track[12] = ["c_0"]

        def mock_random_camel(_):
            return 1

        def mock_roll(move_range):
            return 1

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 0)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[11] = ["c_1", "c_2", "c_3", "c_4"]
                expected_track[12] = ["c_0"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

    def test_move_partial_stack_to_empty(self):
        self.g.camel_track[10] = ["c_1", "c_2", "c_3", "c_4"]
        self.g.camel_track[12] = ["c_0"]

        def mock_random_camel(_):
            return 3

        def mock_roll(_):
            return 1

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 0)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[10] = ["c_1", "c_2"]
                expected_track[11] = ["c_3", "c_4"]
                expected_track[12] = ["c_0"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

    def test_move_one_camel_to_stack(self):
        self.g.camel_track[10] = ["c_0"]
        self.g.camel_track[12] = ["c_1", "c_2", "c_3", "c_4"]

        def mock_random_camel(_):
            return 0

        def mock_roll(_):
            return 2

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 0)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[12] = ["c_1", "c_2", "c_3", "c_4", "c_0"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])
                self.assertEqual(camelup.find_camel_in_nth_place(self.g, 1), "c_0")

    def test_move_stacked_camel_to_stack(self):
        self.g.camel_track[10] = ["c_0", "c_1"]
        self.g.camel_track[12] = ["c_2", "c_3", "c_4"]

        def mock_random_camel(_):
            return 0

        def mock_roll(_):
            return 2

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 0)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[12] = ["c_2", "c_3", "c_4", "c_0", "c_1"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

    def test_move_partial_stack_to_stack(self):
        self.g.camel_track[10] = ["c_0", "c_1", "c_2"]
        self.g.camel_track[12] = ["c_3", "c_4"]

        def mock_random_camel(_):
            return 1

        def mock_roll(_):
            return 2

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 0)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[10] = ["c_0"]
                expected_track[12] = ["c_3", "c_4", "c_1", "c_2"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

    def test_move_one_camel_to_plus_trap_to_empty(self):
        self.g.camel_track[10] = ["c_0"]
        self.g.camel_track[15] = ["c_3", "c_4", "c_2", "c_1"]
        self.g.trap_track[11] = [1, 0]
        expected_player_money = copy.deepcopy(self.g.player_money_values)

        def mock_random_camel(_):
            return 0

        def mock_roll(_):
            return 1

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 2)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[10] = []
                expected_track[12] = ["c_0"]
                expected_track[15] = ["c_3", "c_4", "c_2", "c_1"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[0] += 1
                expected_player_money[2] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)

    def test_move_one_camel_to_plus_trap_to_stack(self):
        self.g.camel_track[10] = ["c_0"]
        self.g.camel_track[12] = ["c_3", "c_4", "c_2", "c_1"]
        self.g.trap_track[11] = [1, 3]
        expected_player_money = copy.deepcopy(self.g.player_money_values)

        def mock_random_camel(_):
            return 0

        def mock_roll(_):
            return 1

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 2)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[10] = []
                expected_track[12] = ["c_3", "c_4", "c_2", "c_1", "c_0"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[3] += 1
                expected_player_money[2] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)

    def test_move_stack_to_plus_trap_to_empty(self):
        self.g.camel_track[8] = ["c_0"]
        self.g.camel_track[10] = ["c_3", "c_4", "c_2", "c_1"]
        self.g.trap_track[11] = [1, 0]
        expected_player_money = copy.deepcopy(self.g.player_money_values)

        def mock_random_camel(_):
            return 3

        def mock_roll(_):
            return 1

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 0)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[8] = ["c_0"]
                expected_track[10] = []
                expected_track[12] = ["c_3", "c_4", "c_2", "c_1"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[0] += 1
                expected_player_money[0] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)

    def test_move_stack_to_plus_trap_to_stack(self):
        self.g.camel_track[8] = ["c_0", "c_2"]
        self.g.camel_track[10] = ["c_3", "c_4", "c_1"]
        self.g.trap_track[9] = [1, 0]
        expected_player_money = copy.deepcopy(self.g.player_money_values)

        def mock_random_camel(_):
            return 0

        def mock_roll(_):
            return 1

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 1)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[8] = []
                expected_track[10] = ["c_3", "c_4", "c_1", "c_0", "c_2"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[0] += 1
                expected_player_money[1] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)

    def test_move_partial_stack_to_plus_trap_to_empty(self):
        self.g.camel_track[8] = ["c_0", "c_2", "c_4"]
        self.g.camel_track[13] = ["c_3", "c_1"]
        self.g.trap_track[9] = [1, 0]
        expected_player_money = copy.deepcopy(self.g.player_money_values)

        def mock_random_camel(_):
            return 2

        def mock_roll(_):
            return 1

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 1)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[8] = ["c_0"]
                expected_track[10] = ["c_2", "c_4"]
                expected_track[13] = ["c_3", "c_1"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[0] += 1
                expected_player_money[1] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)

    def test_move_partial_stack_to_plus_trap_to_stack(self):
        self.g.camel_track[8] = ["c_0", "c_2", "c_4"]
        self.g.camel_track[11] = ["c_3", "c_1"]
        self.g.trap_track[10] = [1, 0]
        expected_player_money = copy.deepcopy(self.g.player_money_values)

        def mock_random_camel(_):
            return 2

        def mock_roll(_):
            return 2

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 3)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[8] = ["c_0"]
                expected_track[11] = ["c_3", "c_1", "c_2", "c_4"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[0] += 1
                expected_player_money[3] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)

    def test_move_one_camel_to_minus_trap_to_empty(self):
        self.g.camel_track[8] = ["c_0"]
        self.g.camel_track[11] = ["c_3", "c_1"]
        self.g.camel_track[14] = ["c_2", "c_4"]
        self.g.trap_track[10] = [-1, 2]
        expected_player_money = copy.deepcopy(self.g.player_money_values)

        def mock_random_camel(_):
            return 0

        def mock_roll(_):
            return 2

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 3)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[8] = []
                expected_track[9] = ["c_0"]
                expected_track[11] = ["c_3", "c_1"]
                expected_track[14] = ["c_2", "c_4"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[2] += 1
                expected_player_money[3] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)

    def test_move_one_camel_to_minus_trap_to_empty_no_change_to_board(self):
        self.g.camel_track[8] = ["c_0"]
        self.g.camel_track[11] = ["c_3", "c_1"]
        self.g.camel_track[14] = ["c_2", "c_4"]
        self.g.trap_track[9] = [-1, 2]
        expected_player_money = copy.deepcopy(self.g.player_money_values)
        expected_track = copy.deepcopy(self.g.camel_track)

        def mock_random_camel(_):
            return 0

        def mock_roll(_):
            return 1

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 3)
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[2] += 1
                expected_player_money[3] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)

    def test_move_one_camel_to_minus_trap_to_stack(self):
        self.g.camel_track[8] = ["c_0"]
        self.g.camel_track[9] = ["c_3", "c_1"]
        self.g.camel_track[14] = ["c_2", "c_4"]
        self.g.trap_track[10] = [-1, 2]
        expected_player_money = copy.deepcopy(self.g.player_money_values)

        def mock_random_camel(_):
            return 0

        def mock_roll(_):
            return 2

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 3)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[8] = []
                expected_track[9] = ["c_0", "c_3", "c_1"]
                expected_track[14] = ["c_2", "c_4"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[2] += 1
                expected_player_money[3] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)

    def test_move_full_stack_to_minus_trap_to_empty(self):
        self.g.camel_track[8] = ["c_0", "c_2", "c_1", "c_4"]
        self.g.camel_track[11] = ["c_3"]
        self.g.trap_track[10] = [-1, 2]
        expected_player_money = copy.deepcopy(self.g.player_money_values)

        def mock_random_camel(_):
            return 0

        def mock_roll(_):
            return 2

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 3)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[8] = []
                expected_track[9] = ["c_0", "c_2", "c_1", "c_4"]
                expected_track[11] = ["c_3"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[2] += 1
                expected_player_money[3] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)

    def test_move_full_stack_to_minus_trap_to_stack(self):
        self.g.camel_track[8] = ["c_0", "c_2", "c_4"]
        self.g.camel_track[9] = ["c_3", "c_1"]
        self.g.trap_track[10] = [-1, 2]
        expected_player_money = copy.deepcopy(self.g.player_money_values)

        def mock_random_camel(_):
            return 0

        def mock_roll(_):
            return 2

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                camelup.move_camel(self.g, 3)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[8] = []
                expected_track[9] = ["c_0", "c_2", "c_4", "c_3", "c_1"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[2] += 1
                expected_player_money[3] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)

    def test_move_partial_stack_to_minus_trap_to_empty(self):
        self.g.camel_track[8] = ["c_0", "c_2", "c_4"]
        self.g.camel_track[12] = ["c_3", "c_1"]
        self.g.trap_track[10] = [-1, 1]
        expected_player_money = copy.deepcopy(self.g.player_money_values)

        def mock_random_camel(_):
            return 2

        def mock_roll(_):
            return 2

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                # camelup.display_track_state(self.g)
                camelup.move_camel(self.g, 3)
                # camelup.display_track_state(self.g)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[8] = ["c_0"]
                expected_track[9] = ["c_2", "c_4"]
                expected_track[12] = ["c_3", "c_1"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[1] += 1
                expected_player_money[3] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)

    def test_move_partial_stack_to_minus_trap_to_stack(self):
        self.g.camel_track[8] = ["c_0", "c_2", "c_4"]
        self.g.camel_track[9] = ["c_3", "c_1"]
        self.g.trap_track[10] = [-1, 1]
        expected_player_money = copy.deepcopy(self.g.player_money_values)

        def mock_random_camel(_):
            return 2

        def mock_roll(_):
            return 2

        with unittest.mock.patch('random.choice', mock_random_camel):
            with unittest.mock.patch('camelup.roll_dice', mock_roll):
                # camelup.display_track_state(self.g)
                camelup.move_camel(self.g, 3)
                # camelup.display_track_state(self.g)
                expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
                expected_track[8] = ["c_0"]
                expected_track[9] = ["c_2", "c_4", "c_3", "c_1"]
                for ii in range(self.g.BOARD_SIZE):
                    self.assertEqual(self.g.camel_track[ii], expected_track[ii])

                # Check that payout occurred
                expected_player_money[1] += 1
                expected_player_money[3] += 1
                self.assertEqual(self.g.player_money_values, expected_player_money)


if __name__ == '__main__':
    unittest.main()
