import camelup
import actionids

from camelup import GameState, get_valid_moves, move_camel, move_trap, place_round_winner_bet, place_game_bet
from actionids import GAME_BET_ACTION_ID, ROUND_BET_ACTION_ID, MOVE_TRAP_ACTION_ID, MOVE_CAMEL_ACTION_ID
from playerinterface import PlayerInterface
import random


class IllegalMoveException(Exception):
    pass


# -------------------- State Representation -------------------- #
def get_state(g : GameState):
    """
    Converts the current GameState into a tuple representation for MDP purposes.
    :param g: GameState object.
    :return: Tuple representing the current state.
    """
    state = (
        tuple(map(tuple, g.camel_track)),
        tuple(map(tuple, g.trap_track)),
        tuple(g.round_bets),
        tuple(g.game_winner_bets),
        tuple(g.game_loser_bets),
        tuple(g.player_money_values),
        tuple(g.camel_yet_to_move)
    )
    return state


# -------------------- Transition Function -------------------- #
def transition(g : GameState, player, action):
    """
    Applies an action to the current state and returns the new state and reward.
    :param g: GameState object.
    :param player: Player ID integer.
    :param action: Action tuple.
    :return: Tuple (new_state, reward).
    """
    initial_money = g.player_money_values[player]  # Track initial coins for reward calculation

    # Apply the action based on its type
    if action[0] == MOVE_CAMEL_ACTION_ID:
        move_camel(g, player)
    elif action[0] == MOVE_TRAP_ACTION_ID:
        _, trap_type, trap_location = action
        move_trap(g, trap_type, trap_location, player)
    elif action[0] == ROUND_BET_ACTION_ID:
        _, camel = action
        place_round_winner_bet(g, camel, player)
    elif action[0] == GAME_BET_ACTION_ID:
        _, bet_type, camel = action
        place_game_bet(g, camel, bet_type, player)
    else:
        raise IllegalMoveException(f"Illegal action {action} for player {player}")

    reward = g.player_money_values[player] - initial_money  # Calculate reward
    new_state = get_state(g)  # Get the new state
    return new_state, reward


# -------------------- Environment Interaction -------------------- #
def mdp_step(g : GameState, player, action):
    """
    Executes an MDP step: applies an action, computes the reward, and updates the game state.
    :param g: GameState object.
    :param player: Player ID integer.
    :param action: Action tuple.
    :return: Tuple (new_state, reward, done).
    """
    new_state, reward = transition(g, player, action)
    done = not g.active_game  # Check if the game has ended
    return new_state, reward, done


# -------------------- Game Simulation -------------------- #
def simulate_game(players : PlayerInterface):
    """
    Simulates a full game using the provided player agents.
    :param players: List of PlayerInterface objects (agents with policies).
    :return: Action log and final game state.
    """
    g = GameState(num_players=len(players))  # Initialize the game
    action_log = []  # Log actions for analysis or training

    while g.active_game:
        for player_id, player in enumerate(players):
            state = get_state(g)
            actions = get_valid_moves(g, player_id)  # Fetch valid actions
            action = player.move(player_id, g.get_player_copy(player_id))  # Choose action based on policy

            if action not in actions:
                raise IllegalMoveException(f"Player {player_id} made an illegal move: {action}")

            new_state, reward, done = mdp_step(g, player_id, action)  # Perform action
            action_log.append({
                "player": player_id,
                "state": state,
                "action": action,
                "new_state": new_state,
                "reward": reward
            })

            if done:  # If the game ends, break out of the loop
                break

    return action_log, g


# -------------------- Example Player Interface -------------------- #
class RandomPlayer(PlayerInterface):
    """
    An example player that chooses actions randomly from the valid moves.
    """

    def move(self, player_id, game_copy):
        actions = get_valid_moves(game_copy, player_id)
        return random.choice(actions)


# -------------------- Example Usage -------------------- #
if __name__ == "__main__":
    # Example players
    players = [RandomPlayer() for _ in range(4)]

    # Simulate the game
    action_log, final_state = simulate_game(players)

    # Print results
    print("Game Over!")
    for log_entry in action_log:
        print(log_entry)
    print("Final State:", final_state)
