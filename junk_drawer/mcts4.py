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
        while time.time() - start_time < 3:
            leaf = self.select(root)
            child = self.expand(leaf)
            result = self.simulate(child)
            self.backpropagate(child, result)

        most_visits = -1
        best_action = None
        children = root.children
        for child in children:
            if child.visits > most_visits:
                most_visits = child.visits
                best_action = child.action
        print(best_action)
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
                #NEW
                if child.visits == 0 or not node.children:
                    return child
                UCB = child.value / child.visits + self.c * \
                    np.sqrt(np.log(node.visits) / child.visits)
                if UCB > best_ucb:
                    best_ucb = UCB
                    best_child = child
            node = best_child
        return node
    
    def expand(self, leaf : MCTSNode):
        if not leaf.state.active_game:
            return leaf
        
        actions = get_valid_moves(leaf.state, leaf.state.active_player)
        min_non_none_index = min([i for i, track in enumerate(leaf.state.camel_track) if track])
        max_non_none_index = max([i for i, track in enumerate(leaf.state.camel_track) if track])
        pruned_actions = []
        for action in actions:
            if action[0] == 1:
                trap_loc = action[2]
                if trap_loc > min_non_none_index and trap_loc <= max_non_none_index + 3:
                    pruned_actions.append(action)
            else:
                pruned_actions.append(action)
        np.random.shuffle(pruned_actions)
        
        #NEW
        if not pruned_actions:
            return leaf
        
        actions = set(pruned_actions)
        already_explored = set([child.action for child in leaf.children])
        actions = actions - already_explored
        actions = list(actions)
        action = actions[np.random.randint(len(actions))]
        new_state = self.transition(leaf.state, action)
        new_node = MCTSNode(new_state, parent=leaf, action=action)
        leaf.children.append(new_node)
        new_node.parent = leaf
        return new_node

    def simulate(self, child : MCTSNode):
        """
        Simulates a random game from the given node's state.
        :param node: Node to simulate from.
        :return: Simulation result (game outcome).
        """
        state = child.state
        while state.active_game:
            actions = get_valid_moves(state, state.active_player)
            #NEW
            if not actions:
                break
            actions = list(actions)
            action = actions[np.random.randint(len(actions))]
            state = self.transition(state, action)
        
        winner = np.argmax(state.player_money_values)
        result = np.zeros(state.NUM_PLAYERS)
        result[winner] = 1
        return result

    def backpropagate(self, child : MCTSNode, result):
        """
        Backpropagates the simulation result through the tree.
        :param node: Leaf node where simulation ended.
        :param result: Result of the simulation.
        """
        node= child
        while node:
            node.visits += 1 
            if result[node.state.active_player] == 1:
                node.value += 1
            node = node.parent

    def transition(self, state: GameState, action):
        new_state = copy.deepcopy(state)
        new_state.verbose = False
        if action[0] == MOVE_CAMEL_ACTION_ID:
            move_camel(new_state, new_state.active_player)
        elif action[0] == MOVE_TRAP_ACTION_ID:
            _, trap_type, trap_location = action
            move_trap(new_state, trap_type, trap_location, new_state.active_player)
        elif action[0] == ROUND_BET_ACTION_ID:
            _, camel = action
            place_round_winner_bet(new_state, camel, new_state.active_player)
        elif action[0] == GAME_BET_ACTION_ID:
            _, bet_type, camel = action
            place_game_bet(new_state, camel, bet_type, new_state.active_player)
        new_state.update_active_player()
        return new_state
