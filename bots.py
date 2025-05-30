from playerinterface import PlayerInterface
from camelup import get_valid_moves, display_game_state
from actionids import GAME_BET_ACTION_ID, ROUND_BET_ACTION_ID, MOVE_TRAP_ACTION_ID, MOVE_CAMEL_ACTION_ID
import random
import numpy as np
from mcts import MCTSAgent as MCTS
from greedy import simulate_round, calculate_round_bet_ev, simulate_race, calculate_race_bet_ev, calculate_rolling_ev, simulate_round_with_traps

class RandomAgent(PlayerInterface):
    """
    This bot randomly choses a move to make. It chooses in a hierarchical fashion, i.e.
    1. Identify which types of moves are available
    2. Choose a type of move, i.e. move camel, place trap, make a game bet, or make a round bet
    3. Randomly select the specific variant of the move to perform, e.g. where to place the trap and what kind it
       should be.
    """
    @staticmethod
    def move(active_player, game_state):
        valid_moves = get_valid_moves(g=game_state, player=active_player)
        valid_super_moves = tuple(set([move[0] for move in valid_moves]))
        random_super_move = random.choice(valid_super_moves)
        possible_moves = [move for move in valid_moves if move[0] == random_super_move]
        return random.choice(possible_moves)

class HumanAgent(PlayerInterface):
    """
    This agent allows a human player to interactively make a move.
    The player is shown all valid moves with specific and descriptive options.
    """
    @staticmethod
    def move(active_player, game_state):
        display_game_state(game_state)
        valid_moves = get_valid_moves(g=game_state, player=active_player)
        
        print("\nAvailable Moves:")
        for index, move in enumerate(valid_moves):
            move_type, *details = move
            if move_type == MOVE_CAMEL_ACTION_ID:
                move_description = f"Move Camel: Roll to move one camel at random and gain one coin" 
            
            elif move_type == MOVE_TRAP_ACTION_ID:
                trap_position = details[1]
                trap_type = "Oasis (+1 space)" if details[0] == 1 else "Mirage (-1 space)"
                move_description = f"Place Trap: Place a {trap_type} trap at position {trap_position}."
            
            elif move_type == GAME_BET_ACTION_ID:
                bet_type = details[0]
                camel_color = details[1]
                move_description = f"Place Game Bet: Bet on {camel_color} to be the overall {'winner' if bet_type == 'win' else 'loser'}"
            
            elif move_type == ROUND_BET_ACTION_ID:
                camel_color = details[0]
                move_description = f"Place Round Bet: Bet that the {camel_color} camel will be leading at the end of this round."

            else:
                move_description = "Unknown Move Type"
                
            print(f"{index}: {move_description}")

        while True:
            try:
                user_input = int(input("\nEnter the number corresponding to the move you want to make: "))
                if 0 <= user_input < len(valid_moves):
                    return valid_moves[user_input]
                else:
                    print(f"Invalid input. Please enter a number between 0 and {len(valid_moves) - 1}.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

class MCTSAgent(PlayerInterface):
    @staticmethod
    def move(active_player, game_state):
        agent = MCTS()
        return agent.get_move(active_player, game_state)
    
class RoundBetAgent(PlayerInterface):
    @staticmethod
    def move(active_player, game_state):
        probabilities = simulate_round(game_state, active_player)
        
        valid_moves = get_valid_moves(game_state, active_player)
        round_bets = [move for move in valid_moves if move[0] == ROUND_BET_ACTION_ID]
        
        if not round_bets:
            return (0, )
        
        best_ev = float('-inf')
        best_move = None
        for bet in round_bets:
            camel = bet[1]  
            ev = calculate_round_bet_ev(game_state, probabilities, camel)
            if ev > best_ev:
                best_ev = ev
                best_move = bet
        # print(best_move)
        return best_move
    
class TrapAgent(PlayerInterface):
    @staticmethod
    def move(active_player, game_state):
        valid_moves = get_valid_moves(game_state, active_player)
        trap_bets = [move for move in valid_moves if move[0] == MOVE_TRAP_ACTION_ID]
        
        if not trap_bets:
            return (0, )
        
        best_ev = float('-inf')
        best_move = None
        for bet in trap_bets:
            trap_type = bet[1]
            trap_position = bet[2]
            ev = simulate_round_with_traps(game_state, active_player, trap_type, trap_position)
            if ev > best_ev:
                best_ev = ev
                best_move = bet
        # print(best_move)
        return best_move
    
class GameBetAgent(PlayerInterface):
    @staticmethod
    def move(active_player, game_state):
        probabilities = simulate_race(game_state, active_player)
        
        valid_moves = get_valid_moves(game_state, active_player)
        trap_bets = [move for move in valid_moves if move[0] == GAME_BET_ACTION_ID]
        
        if not trap_bets:
            return (0, )
        
        best_ev = float('-inf')
        best_move = None
        for bet in trap_bets:
            bet_type = bet[1]  
            camel = bet[2]
            ev = calculate_race_bet_ev(game_state, probabilities, camel, bet_type)
            if ev > best_ev:
                best_ev = ev
                best_move = bet
        # print(best_move)
        return best_move
    
class RollAgent(PlayerInterface):
    @staticmethod
    def move(active_player, game_state):
        return (0,)
    
class GreedyAgent(PlayerInterface):
    @staticmethod
    def move(active_player, game_state):
        probabilities_round = simulate_round(game_state, active_player)
        probabilities_race = simulate_race(game_state, active_player)

        valid_moves = get_valid_moves(game_state, active_player)
        # np.random.shuffle(valid_moves)
        best_ev = float('-inf')
        best_move = None

        for move in valid_moves:
            if move[0] == ROUND_BET_ACTION_ID:
                camel = move[1]
                ev = calculate_round_bet_ev(game_state, probabilities_round, camel)
                # print(f"Round Bet, Camel : {camel}, EV : {ev}")

            elif move[0] == MOVE_CAMEL_ACTION_ID:
                ev = calculate_rolling_ev()
                # print(f"Roll, EV : {ev}")

            elif move[0] == GAME_BET_ACTION_ID:
                bet_type = move[1]  
                camel = move[2]
                ev = calculate_race_bet_ev(game_state, probabilities_race, camel, bet_type)
                # print(f"Game Bet, Camel : {camel}, Bet Type : {bet_type} EV : {ev}")

            elif move[0] == MOVE_TRAP_ACTION_ID:
                trap_type = move[1]
                trap_position = move[2]
                ev = simulate_round_with_traps(game_state, active_player, trap_type, trap_position)
                # print(f"Trap, Trap Type : {trap_type}, Trap Position : {trap_position} EV : {ev}")
            
            else:
                continue

            # print(move, ev)
            if ev > best_ev:
                best_ev = ev
                best_move = move

        return best_move if best_move is not None else (0,)
    
import numpy as np
from playerinterface import PlayerInterface
from camelup import get_valid_moves

from greedy import (
    simulate_round,
    simulate_race,
    calculate_round_bet_ev,
    calculate_race_bet_ev,
    calculate_rolling_ev,
    simulate_round_with_traps
)

import numpy as np
from playerinterface import PlayerInterface
from camelup import get_valid_moves

from greedy import (
    simulate_round,
    simulate_race,
    calculate_round_bet_ev,
    calculate_race_bet_ev,
    calculate_rolling_ev,
    simulate_round_with_traps
)

import numpy as np
from playerinterface import PlayerInterface
from camelup import get_valid_moves

from greedy import (
    simulate_round,
    simulate_race,
    calculate_round_bet_ev,
    calculate_race_bet_ev,
    calculate_rolling_ev,
    simulate_round_with_traps
)

# import numpy as np
# import random
# from playerinterface import PlayerInterface
# from camelup import get_valid_moves
# from greedy import (
#     simulate_round,
#     simulate_race,
#     calculate_round_bet_ev,
#     calculate_race_bet_ev,
#     calculate_rolling_ev,
#     simulate_round_with_traps
# )
# from actionids import ROUND_BET_ACTION_ID, MOVE_CAMEL_ACTION_ID, GAME_BET_ACTION_ID, MOVE_TRAP_ACTION_ID

# class DynamicGreedyAgent(PlayerInterface):
#     BASE_VOL = 0.0
#     SCALE = 0.05
#     MAX_VOL = 0.5

#     @staticmethod
#     def move(active_player, game_state):
#         def get_deficit():
#             player_score = game_state.player_money_values[active_player]
#             max_other_score = max(
#                 coins for i, coins in enumerate(game_state.player_money_values) if i != active_player
#             )
#             return max(0, max_other_score - player_score)

#         def get_volatility_score(ev, max_payout):
#             return max_payout - ev

#         round_probs = simulate_round(game_state, active_player)
#         race_probs = simulate_race(game_state, active_player)
#         valid_moves = get_valid_moves(game_state, active_player)

#         deficit = get_deficit()
#         vol_multiplier = min(
#             DynamicGreedyAgent.MAX_VOL,
#             DynamicGreedyAgent.BASE_VOL + DynamicGreedyAgent.SCALE * deficit
#         )
#         print(vol_multiplier)

#         scores = []
#         actions = []

#         for move in valid_moves:
#             if move[0] == ROUND_BET_ACTION_ID:
#                 camel = move[1]
#                 ev = calculate_round_bet_ev(game_state, round_probs, camel)
#                 prob_first = round_probs[camel]["first"]

#                 if prob_first == 0:
#                     max_payout = 0
#                 else:
#                     num_bets = len([bet for bet in game_state.round_bets if bet[0] == camel])
#                     max_payout = game_state.FIRST_PLACE_ROUND_PAYOUT[
#                         num_bets] if num_bets < len(game_state.FIRST_PLACE_ROUND_PAYOUT) else 0

#             elif move[0] == MOVE_CAMEL_ACTION_ID:
#                 ev = calculate_rolling_ev()
#                 max_payout = 1

#             elif move[0] == GAME_BET_ACTION_ID:
#                 bet_type = move[1]
#                 camel = move[2]
#                 ev = calculate_race_bet_ev(game_state, race_probs, camel, bet_type)
#                 prob_win = race_probs[camel]["win"] if bet_type == "win" else race_probs[camel]["lose"]

#                 if prob_win == 0:
#                     max_payout = 0
#                 else:
#                     max_payout = game_state.GAME_END_PAYOUT[0] if game_state.GAME_END_PAYOUT else 0

#             elif move[0] == MOVE_TRAP_ACTION_ID:
#                 trap_type = move[1]
#                 trap_position = move[2]
#                 ev = simulate_round_with_traps(game_state, active_player, trap_type, trap_position)
#                 max_payout = 0

#             else:
#                 continue

#             volatility_score = get_volatility_score(ev, max_payout)
#             score = ev + vol_multiplier * volatility_score

#             actions.append(move)
#             scores.append(score)

#         if not scores:
#             return (0,)

#         best_index = np.argmax(scores)
#         return actions[best_index]
