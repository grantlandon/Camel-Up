import unittest
import copy
import camelup


class MoveTrapTest(unittest.TestCase):

    def setUp(self):
        self.g = camelup.GameState()

        # Remove camels from start positions
        self.g.camel_track[0] = []
        self.g.camel_track[1] = []
        self.g.camel_track[2] = []

    def test_place_new_trap_successful(self):
        camelup.move_trap(self.g, 1, 5, 2)
        expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
        expected_track[5] = [1, 2]
        for ii in range(self.g.BOARD_SIZE):
            self.assertEqual(self.g.trap_track[ii], expected_track[ii])

        self.assertTrue(self.g.has_player_placed_trap(2))

    def test_place_new_trap_on_existing_trap(self):
        self.g.trap_track[5] = [-1, 3]
        self.assertRaises(ValueError, camelup.move_trap, self.g, 1, 5, 2)
        self.assertTrue(self.g.has_player_placed_trap(3))
        self.assertFalse(self.g.has_player_placed_trap(2))

    def test_place_new_trap_next_to_existing_trap(self):
        self.g.trap_track[5] = [-1, 3]
        self.assertRaises(ValueError, camelup.move_trap, self.g, 1, 6, 2)
        self.assertTrue(self.g.has_player_placed_trap(3))

    def test_place_trap_on_first_field(self):
        self.assertRaises(ValueError, camelup.move_trap, self.g, 1, 0, 2)
        self.assertFalse(self.g.has_player_placed_trap(2))

    def test_move_trap_to_empty_spot(self):
        self.g.trap_track[10] = [-1, 1]
        camelup.move_trap(self.g, 1, 8, 1)
        self.assertTrue(self.g.has_player_placed_trap(1))
        expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
        expected_track[8] = [1, 1]
        for ii in range(self.g.BOARD_SIZE):
            self.assertEqual(self.g.trap_track[ii], expected_track[ii])

    def test_move_trap_to_occupied_spot(self):
        self.g.trap_track[10] = [-1, 1]
        self.g.trap_track[5] = [1, 2]
        self.assertRaises(ValueError, camelup.move_trap, self.g, 1, 10, 2)
        self.assertTrue(self.g.has_player_placed_trap(1))
        self.assertTrue(self.g.has_player_placed_trap(2))

    def test_move_trap_next_to_occupied_spot(self):
        self.g.trap_track[10] = [-1, 1]
        self.g.trap_track[5] = [1, 2]
        self.assertRaises(ValueError, camelup.move_trap, self.g, 1, 9, 2)
        self.assertTrue(self.g.has_player_placed_trap(1))
        self.assertTrue(self.g.has_player_placed_trap(2))

    def test_move_trap_next_to_itself(self):
        self.g.trap_track[10] = [-1, 1]
        self.g.trap_track[5] = [1, 2]
        camelup.move_trap(self.g, 1, 6, 2)
        self.assertTrue(self.g.has_player_placed_trap(1))
        self.assertTrue(self.g.has_player_placed_trap(2))
        expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
        expected_track[10] = [-1, 1]
        expected_track[6] = [1, 2]
        for ii in range(self.g.BOARD_SIZE):
            self.assertEqual(self.g.trap_track[ii], expected_track[ii])

    def test_move_trap_onto_itself(self):
        self.g.trap_track[10] = [-1, 1]
        self.g.trap_track[5] = [1, 2]
        self.assertRaises(ValueError, camelup.move_trap, self.g, 1, 5, 2)
        self.assertTrue(self.g.has_player_placed_trap(1))
        self.assertTrue(self.g.has_player_placed_trap(2))

    def test_flip_trap_type(self):
        self.g.trap_track[10] = [1, 1]
        self.g.trap_track[5] = [1, 2]
        camelup.move_trap(self.g, -1, 10, 1)
        self.assertTrue(self.g.has_player_placed_trap(1))
        self.assertTrue(self.g.has_player_placed_trap(2))
        expected_track = [[] for _ in range(self.g.BOARD_SIZE * 2)]
        expected_track[10] = [-1, 1]
        expected_track[5] = [1, 2]
        for ii in range(self.g.BOARD_SIZE):
            self.assertEqual(self.g.trap_track[ii], expected_track[ii])

    def test_place_trap_on_camel(self):
        self.g.camel_track[10] = ["c_1"]
        self.g.camel_track[12] = ["c_2", "c_3"]
        self.assertRaises(ValueError, camelup.move_trap, self.g, 1, 10, 2)
        self.assertRaises(ValueError, camelup.move_trap, self.g, 1, 12, 3)
        self.assertFalse(self.g.has_player_placed_trap(2))
        self.assertFalse(self.g.has_player_placed_trap(3))

    def test_move_trap_on_camel(self):
        self.g.trap_track[4] = [1, 2]
        self.g.camel_track[10] = ["c_1"]
        self.g.camel_track[12] = ["c_2", "c_3"]
        self.assertRaises(ValueError, camelup.move_trap, self.g, 1, 10, 2)
        self.assertTrue(self.g.has_player_placed_trap(2))


if __name__ == '__main__':
    unittest.main()
