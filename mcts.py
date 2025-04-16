import numpy as np
from camelup import get_valid_moves, GameState, move_camel, move_trap, place_round_winner_bet, place_game_bet
from actionids import *
import copy
import time

class MCTSNode:
    def __init__(self, state: GameState, ptm=None, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0 
        self.value = 0
        self.player_to_move = ptm
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
        root = MCTSNode(game_state, ptm=active_player)
        start_time = time.time()
        while time.time() - start_time < 2:
            leaf = self.select(root)
            children = self.expand(leaf)
            results = self.simulate(children)
            self.backpropagate(children, results)

        most_visits = -1
        best_action = None
        children = root.children
        np.random.shuffle(children)
        # print(children)
        for child in children:
            if child.visits > most_visits:
                most_visits = child.visits
                best_action = child.action
        # print(best_action)
        return best_action

    def select(self, node : MCTSNode):
        """
        Select the child node to expand using the UCB1 formula.
        :param node: Current node.
        :return: Selected node.
        """
        best_ucb = -float('inf')
        best_child = None
        while node.state.active_game and node.children:
            if node.visits == 0 or not node.children:
                return node
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

    def expand(self, leaf : MCTSNode):
        """
        Expands a node by adding a child for an unexplored action.
        :param leaf: Node to expand.
        :return: Newly created child node.
        """
        if not leaf.state.active_game:
            return [leaf] 
        
        actions = get_valid_moves(leaf.state, leaf.player_to_move)
        # min_non_none_index = min([i for i, track in enumerate(leaf.state.camel_track) if track])
        # max_non_none_index = max([i for i, track in enumerate(leaf.state.camel_track) if track])
        # pruned_actions = []
        # for action in actions:
        #     if action[0] == 1:
        #         trap_loc = action[2]
        #         if trap_loc > min_non_none_index and trap_loc <= max_non_none_index + 3:
        #             pruned_actions.append(action)
        #     else:
        #         pruned_actions.append(action)
                    
                    
        np.random.shuffle(actions)
        children = []
        for action in actions:
            new_state = self.transition(leaf.state, leaf.player_to_move, action)
            new_ptm = (leaf.player_to_move + 1) % leaf.state.NUM_PLAYERS
            new_node = MCTSNode(new_state, ptm=new_ptm, parent=leaf, action=action)
            leaf.children.append(new_node)
            children.append(new_node)
            new_node.parent = leaf
            
        return children

    def simulate(self, children):
        """
        Simulates a random game from the given node's state.
        :param node: Node to simulate from.
        :return: Simulation result (game outcome).
        """
        results = []
        for child in children:
            state = child.state
            current_player = child.player_to_move
            while state.active_game:
                actions = get_valid_moves(state, current_player)
                actions = list(actions)
                action = actions[np.random.randint(len(actions))]
                state = self.transition(state, current_player, action)
                current_player = (current_player + 1) % state.NUM_PLAYERS
            
            winner = np.argmax(state.player_money_values)
            result = np.zeros(state.NUM_PLAYERS)
            result[winner] = 1
            results.append(result) 
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
                if result[node.player_to_move] == 1:
                    node.value += 1
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
