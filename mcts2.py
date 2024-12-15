import numpy as np
from camelup import get_valid_moves, GameState, move_camel, move_trap, place_round_winner_bet, place_game_bet
from actionids import *
import copy
import time

class MCTSNode:
    def __init__(self, state: GameState, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0
        self.action = action

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Node: {self.state} \nVisits: {self.visits} \nValue: {self.value} \nParent: {self.parent}"

class MCTSAgent:
    def __init__(self, c=np.sqrt(2)):
        """
        Monte Carlo Tree Search Agent.
        :param c: Exploration parameter for UCB.
        """
        self.c = c

    def get_move(self, active_player, game_state):
        """
        Executes the MCTS algorithm to determine the best move.
        :param active_player: The ID of the active player.
        :param game_state: The current GameState.
        :return: The best action to take.
        """
        root = MCTSNode(game_state)
        start_time = time.time()
        while time.time() - start_time < 1.5:
            leaf = self.select(root, active_player)
            children = self.expand(leaf, active_player)
            results = self.simulate(children, active_player)
            self.backpropagate(children, results)

        # Choose the action of the most visited child node
        most_visits = -1
        best_action = None
        children = root.children
        np.random.shuffle(children)
        for child in children:
            if child.visits > most_visits:
                most_visits = child.visits
                best_action = child.action
        # print(best_action)
        return best_action

    def select(self, node, active_player):
        """
        Select the child node to expand using the UCB1 formula.
        :param node: Current node.
        :param active_player: The ID of the active player.
        :return: Selected node.
        """
        best_ucb = -float('inf')
        best_child = None
        while node.state.active_game and node.children and len(get_valid_moves(node.state, active_player)) != 0:
            # if len(get_valid_moves(node.state, active_player)) == 0:
            #     # If no legal actions, game is over
            #     return node
            # if len(node.children) < len(get_valid_moves(node.state, active_player)):
            #     # If not fully expanded, is leaf
            #     return node
            best_ucb = -float('inf')
            best_child = None
            for child in node.children:
                UCB = child.value / child.visits + self.c * \
                    np.sqrt(np.log(node.visits) / child.visits)
                if UCB > best_ucb:
                    best_ucb = UCB
                    best_child = child
            node = best_child
        return node

    def expand(self, leaf, active_player):
        """
        Expands a node by adding a child for an unexplored action.
        :param leaf: Node to expand.
        :param active_player: The ID of the active player.
        :return: Newly created child node.
        """
        if not leaf.state.active_game:
            return [leaf]  # Return the leaf if the game is over
        actions = get_valid_moves(leaf.state, active_player)
        np.random.shuffle(actions)
        children = []
        for action in actions:
            new_state = self.transition(leaf.state, active_player, action)
            new_node = MCTSNode(new_state, parent=leaf, action=action)
            leaf.children.append(new_node)
            children.append(new_node)
            new_node.parent = leaf
        return children

    def simulate(self, children, active_player):
        """
        Simulates a random game from the given node's state.
        :param node: Node to simulate from.
        :param active_player: The ID of the active player.
        :return: Simulation result (game outcome).
        """
        results = []
        for child in children:
            state = child.state
            current_player = active_player
            while state.active_game:
                actions = get_valid_moves(state, current_player)
                actions = list(actions)
                action = actions[np.random.randint(len(actions))]
                state = self.transition(state, current_player, action)
                current_player = (current_player + 1) % state.NUM_PLAYERS
            if state.player_money_values[active_player] == max(state.player_money_values):
                results.append(1) 
            else:
                results.append(0) 
        return results

    def backpropagate(self, children, results):
        """
        Backpropagates the simulation result through the tree.
        :param node: Leaf node where simulation ended.
        :param result: Result of the simulation.
        """
        for child, result in zip(children, results):
            node = child
            while node:
                node.visits += 1
                node.value += result
                node = node.parent

    def transition(self, state : GameState, player, action):
        """
        Applies an action to a GameState and returns the resulting state.
        :param state: Current GameState.
        :param player: Player performing the action.
        :param action: Action to apply.
        :return: New GameState after the action.
        """
        new_state = GameState(
            num_camels=state.NUM_CAMELS,
            num_players=state.NUM_PLAYERS,
            board_size=state.BOARD_SIZE,
            move_range=state.MOVE_RANGE,
            first_place_round_payout=state.FIRST_PLACE_ROUND_PAYOUT,
            second_place_round_payout=state.SECOND_PLACE_ROUND_PAYOUT,
            third_or_worse_place_round_payout=state.THIRD_OR_WORSE_PLACE_ROUND_PAYOUT,
            game_end_payout=state.GAME_END_PAYOUT,
            bad_game_end_bet=state.BAD_GAME_END_BET,
            verbose=False
        )
        new_state.camel_track = copy.deepcopy(state.camel_track)
        new_state.trap_track = copy.deepcopy(state.trap_track)
        new_state.round_bets = copy.deepcopy(state.round_bets)
        new_state.game_winner_bets = copy.deepcopy(state.game_winner_bets)
        new_state.game_loser_bets = copy.deepcopy(state.game_loser_bets)
        new_state.player_money_values = copy.deepcopy(state.player_money_values)
        new_state.camel_yet_to_move = copy.deepcopy(state.camel_yet_to_move)

        # Apply the action
        if action[0] == MOVE_CAMEL_ACTION_ID:
            move_camel(new_state, player)
        elif action[0] == MOVE_TRAP_ACTION_ID:
            _, trap_type, trap_location = action
            move_trap(new_state, trap_type, trap_location, player)
        elif action[0] == ROUND_BET_ACTION_ID:
            _, camel = action
            place_round_winner_bet(new_state, camel, player)
        elif action[0] == GAME_BET_ACTION_ID:
            _, bet_type, camel = action
            place_game_bet(new_state, camel, bet_type, player)
        return new_state
