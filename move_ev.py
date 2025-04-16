import pandas as pd
import os
import tqdm
import random
import copy
from camelup import GameState, summarize_game_state, get_valid_moves, move_camel, move_trap, place_round_winner_bet, place_game_bet, end_of_round, end_of_game, display_game_state
from actionids import MOVE_CAMEL_ACTION_ID, MOVE_TRAP_ACTION_ID, ROUND_BET_ACTION_ID, GAME_BET_ACTION_ID
from greedy import simulate_round, simulate_race, calculate_round_bet_ev, calculate_race_bet_ev, calculate_rolling_ev, simulate_round_with_traps

class InlineGreedyAgent:
    @staticmethod
    def move(active_player, game_state):
        probabilities_round = simulate_round(game_state, active_player)
        probabilities_race = simulate_race(game_state, active_player)
        valid_moves = get_valid_moves(game_state, active_player)

        best_ev = float('-inf')
        best_move = None

        for move in valid_moves:
            if move[0] == ROUND_BET_ACTION_ID:
                camel = move[1]
                ev = calculate_round_bet_ev(game_state, probabilities_round, camel)

            elif move[0] == MOVE_CAMEL_ACTION_ID:
                ev = calculate_rolling_ev()

            elif move[0] == GAME_BET_ACTION_ID:
                bet_type = move[1]  
                camel = move[2]
                ev = calculate_race_bet_ev(game_state, probabilities_race, camel, bet_type)

            elif move[0] == MOVE_TRAP_ACTION_ID:
                trap_type = move[1]
                trap_position = move[2]
                ev = simulate_round_with_traps(game_state, active_player, trap_type, trap_position)

            else:
                continue

            if ev > best_ev:
                best_ev = ev
                best_move = move

        return (best_move if best_move is not None else (0,)), best_ev

def action(result, player, g):
    action_params = {}
    if result[0] == MOVE_CAMEL_ACTION_ID:
        camel, distance = move_camel(g, player)
        action_params["action_type"] = "move_camel"
        action_params["camel"] = camel
        action_params["distance"] = distance

    elif result[0] == MOVE_TRAP_ACTION_ID:
        move_trap(g, result[1], result[2], player)
        action_params["action_type"] = "move_trap"
        action_params["trap_type"] = result[1]
        action_params["trap_location"] = result[2]

    elif result[0] == ROUND_BET_ACTION_ID:
        place_round_winner_bet(g, result[1], player)
        action_params["action_type"] = "round_winner_bet"
        action_params["camel"] = result[1]

    elif result[0] == GAME_BET_ACTION_ID:
        place_game_bet(g, result[2], result[1], player)
        action_params["action_type"] = "game_bet"
        action_params["bet_type"] = result[1]
        action_params["camel"] = result[2]

    else:
        raise ValueError("Illegal action ({}) performed by player {}".format(result, player))
    return action_params

def play_game(players):
    g = GameState(num_players=len(players))
    g_round = 0
    action_log = [{"round_id": g_round, **summarize_game_state(g)}]

    while g.active_game:
        active_player = (g_round % len(players))
        player_move_result = players[active_player].move(active_player, g.get_player_copy(active_player))

        if isinstance(player_move_result, tuple) and isinstance(player_move_result[0], tuple):
            player_action, ev = player_move_result
        else:
            player_action = player_move_result
            ev = None

        if player_action not in get_valid_moves(g=g, player=active_player):
            raise ValueError("Player {} made an illegal move".format(active_player))

        action_summary = action(result=player_action, player=active_player, g=g)
        action_summary["ev"] = ev
        g_round += 1
        display_game_state(g)

        action_log.append({
            "round_id": g_round,
            "active_player": active_player,
            **action_summary,
            **summarize_game_state(g)
        })

    return action_log, g

def run_ev_tracking_simulation(num_games=200, log_file_path="game_logs/GreedyActionEVLog.csv"):
    os.makedirs("game_logs", exist_ok=True)
    all_game_logs = []

    for game_id in tqdm.tqdm(range(num_games), desc="Simulating games"):
        game_log, final_state = play_game(players=[InlineGreedyAgent] * 4)
        for step in game_log:
            step["game_id"] = game_id
        all_game_logs.extend(game_log)

    df = pd.DataFrame(all_game_logs)
    df.to_csv(log_file_path, index=False)
    print(f"Saved EV logs to {log_file_path}")

if __name__ == "__main__":
    run_ev_tracking_simulation(num_games=100)
