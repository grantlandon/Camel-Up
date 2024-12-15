import random
import copy
from camelup import (
    get_valid_moves,
    GameState,
    move_camel,
    move_trap,
    place_game_bet,
    place_round_winner_bet,
    find_camel_in_nth_place
)
from playerinterface import PlayerInterface
from actionids import MOVE_CAMEL_ACTION_ID, ROUND_BET_ACTION_ID, GAME_BET_ACTION_ID, MOVE_TRAP_ACTION_ID

# ROUND BETTING

def simulate_round(game_state, active_player, num_simulations=1000):
    """
    Simulates the rest of the current round num_simulations times to estimate camel probabilities.
    :param game_state: The current game state.
    :param num_simulations: Number of simulations to run.
    :return: A dictionary with probabilities for each camel finishing first or second.
    """
    camel_counts = {camel: {"first": 0, "second": 0} for camel in game_state.CAMELS}
    
    current_player = active_player
    for _ in range(num_simulations):
        state = game_state
        while not all(state.camel_yet_to_move):  # Continue until all camels have moved
            if not state.active_game:
                break
            roll_id = (0,)
            state = transition(state, current_player, roll_id)
            current_player = (current_player + 1) % state.NUM_PLAYERS
        
        # Determine first and second place camels
        first_place_camel = find_camel_in_nth_place(state, 1)
        second_place_camel = find_camel_in_nth_place(state, 2)
        
        camel_counts[first_place_camel]["first"] += 1
        camel_counts[second_place_camel]["second"] += 1
    
    total_simulations = num_simulations
    probabilities = {
        camel: {
            "first": camel_counts[camel]["first"] / total_simulations,
            "second": camel_counts[camel]["second"] / total_simulations
        }
        for camel in game_state.CAMELS
    }
    
    return probabilities

def get_round_bet_payout(game_state, camel, place):
    """
    Get the payout for betting on a camel to finish in a specific place during the round.
    :param game_state: The current game state.
    :param camel: The camel ID (e.g., "c_1").
    :param place: The place to evaluate (1 for first, 2 for second, etc.).
    :return: The payout for betting on the camel to finish in the given place.
    """
    # Determine the number of bets already placed on this camel
    num_bets = len([bet for bet in game_state.round_bets if bet[0] == camel])
    
    # Handle first, second, and third-or-worse payouts
    if place == 1:  # First place
        if num_bets < len(game_state.FIRST_PLACE_ROUND_PAYOUT):
            return game_state.FIRST_PLACE_ROUND_PAYOUT[num_bets]
        else:
            return 0  # No payout if too many bets have already been placed
    
    elif place == 2:  # Second place
        if num_bets < len(game_state.SECOND_PLACE_ROUND_PAYOUT):
            return game_state.SECOND_PLACE_ROUND_PAYOUT[num_bets]
        else:
            return 0  # No payout if too many bets have already been placed
    
    else:  # Third or worse
        return game_state.THIRD_OR_WORSE_PLACE_ROUND_PAYOUT


def calculate_round_bet_ev(game_state, probabilities, camel):
    """
    Calculate the expected value of betting on a given camel for the round.
    :param game_state: The current game state.
    :param probabilities: A dictionary with probabilities for each camel finishing first or second.
    :param camel: The camel to evaluate.
    :return: Expected value of betting on this camel.
    """
    prob_first = probabilities[camel]["first"]
    prob_second = probabilities[camel]["second"]
    prob_third_or_worse = 1 - prob_first - prob_second

    payout_first = get_round_bet_payout(game_state, camel, place=1)
    payout_second = get_round_bet_payout(game_state, camel, place=2)
    payout_third_or_worse = get_round_bet_payout(game_state, camel, place=3)

    # Calculate EV using payouts and probabilities
    ev = (prob_first * payout_first +
          prob_second * payout_second +
          prob_third_or_worse * payout_third_or_worse)
    return ev

# END ROUND BETTING


# ROLLING

def calculate_rolling_ev(gamma = 0.75):
    return gamma

# END ROLLING

# RACE BETTING

def simulate_race(game_state, active_player, num_simulations=500):
    """
    Simulates the rest of the current round num_simulations times to estimate camel probabilities.
    :param game_state: The current game state.
    :param num_simulations: Number of simulations to run.
    :return: A dictionary with probabilities for each camel finishing first or second.
    """
    camel_counts = {camel: {"win": 0, "lose": 0} for camel in game_state.CAMELS}
    
    current_player = active_player
    for _ in range(num_simulations):
        state = game_state
        while state.active_game:  # Continue until game ends
            roll_id = (0,)
            state = transition(state, current_player, roll_id)
            current_player = (current_player + 1) % state.NUM_PLAYERS
        
        # Determine first and second place camels
        first_place_camel = find_camel_in_nth_place(state, 1)
        last_place_camel = find_camel_in_nth_place(state, state.NUM_CAMELS)
        
        camel_counts[first_place_camel]["win"] += 1
        camel_counts[last_place_camel]["lose"] += 1
    
    total_simulations = num_simulations
    probabilities = {
        camel: {
            "win": camel_counts[camel]["win"] / total_simulations,
            "lose": camel_counts[camel]["lose"] / total_simulations
        }
        for camel in game_state.CAMELS
    }
    
    return probabilities

def get_race_bet_payout(game_state : GameState, camel, bet_type):
    """
    Get the payout for betting on a camel to finish as the overall winner or loser.
    :param game_state: The current game state.
    :param camel: The camel ID (e.g., "c_1").
    :param bet_type: The type of bet ("winner" or "loser").
    :return: The payout for betting on the camel to finish as the overall winner or loser.
    """
    # Determine the number of bets already placed on this camel
    if bet_type == 'win':
        num_bets = len([bet for bet in game_state.game_winner_bets if bet[0] == camel])
    else:
        num_bets = len([bet for bet in game_state.game_loser_bets if bet[0] == camel])
    
    # handle overall winner payouts
    if bet_type == "win":  # overall winner
        if num_bets < len(game_state.GAME_END_PAYOUT):
            return game_state.GAME_END_PAYOUT[num_bets]
        else:
            return game_state.GAME_END_PAYOUT[-1] 
    
    elif bet_type == "lose":  # overall loser
        if num_bets < len(game_state.GAME_END_PAYOUT):
            return game_state.GAME_END_PAYOUT[num_bets]
        else:
            return game_state.GAME_END_PAYOUT[-1] 
    
    return -1

def calculate_race_bet_ev(game_state, probabilities, camel, bet_type):
    """
    Calculate the expected value of betting on a given camel for the round.
    :param game_state: The current game state.
    :param probabilities: A dictionary with probabilities for each camel finishing first or second.
    :param camel: The camel to evaluate.
    :return: Expected value of betting on this camel.
    """
    if bet_type == 'win':
        inv_bet_type = 'lose'
    else:
        inv_bet_type = 'win'
    prob_correct = probabilities[camel][bet_type]
    prob_inv_true = probabilities[camel][inv_bet_type]
    prob_incorrect = 1 - prob_correct - prob_inv_true

    payout = get_race_bet_payout(game_state, camel, bet_type)
    inv_payout = get_race_bet_payout(game_state, camel, inv_bet_type)

    # Calculate EV using payouts and probabilities
    ev = (prob_correct * payout + prob_incorrect * (-1) + prob_inv_true * (-inv_payout))
    return ev


# END RACE BETTING

# TRAPS

def simulate_round_with_traps(game_state : GameState, active_player, trap_type, trap_position, num_simulations=500):
    """
    Simulates the rest of the current round num_simulations times to estimate camel probabilities.
    :param game_state: The current game state.
    :param num_simulations: Number of simulations to run.
    :return: A dictionary with probabilities for each camel finishing first or second.
    """
    min_non_none_index = min([i for i, track in enumerate(game_state.camel_track) if track])
    max_non_none_index = max([i for i, track in enumerate(game_state.camel_track) if track])
    if trap_position < min_non_none_index or max_non_none_index - trap_position > 3:
        return 0
    
    current_player = active_player
    money_no_trap = 0
    
    for _ in range(num_simulations // 2):
        state = game_state
        while not all(state.camel_yet_to_move):  # Continue until all camels have moved
            if not state.active_game:
                break
            roll_id = (0,)
            state = transition(state, current_player, roll_id)
            current_player = (current_player + 1) % state.NUM_PLAYERS
        money_no_trap += state.player_money_values[active_player]
        
    avg_money_no_trap =  money_no_trap / (num_simulations // 2)
    
    #adding trap
    
    current_player = active_player
    money_with_trap = 0
    state = game_state
    start_state_with_trap = transition(state, current_player, (MOVE_TRAP_ACTION_ID, trap_type, trap_position))
    for _ in range(num_simulations // 2):
        state = start_state_with_trap
        while not all(state.camel_yet_to_move):  # Continue until all camels have moved
            if not state.active_game:
                break
            roll_id = (0,)
            state = transition(state, current_player, roll_id)
            current_player = (current_player + 1) % state.NUM_PLAYERS
        money_with_trap += state.player_money_values[active_player]
        
    avg_money_with_trap =  money_with_trap / (num_simulations // 2)
    
    return avg_money_with_trap - avg_money_no_trap

# END TRAPS

def transition(state : GameState, player, action):
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

