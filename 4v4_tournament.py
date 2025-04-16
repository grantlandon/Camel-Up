import os
import random
import pandas as pd
from tqdm import tqdm
from itertools import permutations
from camelup import play_game
from bots import (
    RandomAgent, MCTSAgent, RoundBetAgent, TrapAgent,
    GameBetAgent, RollAgent, GreedyAgent
)

bot_classes = {
    "RandomAgent": RandomAgent,
    "MCTSAgent": MCTSAgent,
    "RoundBetAgent": RoundBetAgent,
    "TrapBetAgent": TrapAgent,
    "GameBetAgent": GameBetAgent,
    "RollAgent": RollAgent,
    "GreedyAgent": GreedyAgent,
}

output_dir = "four_player_tournament_pt2"
os.makedirs(output_dir, exist_ok=True)

def run_random_4player(num_games=10000):
    print("Running: random_4player")
    logs = []

    for game_num in tqdm(range(num_games), desc="random_4player"):
        labels = ["RandomAgent"] * 4
        players = [RandomAgent] * 4
        random.shuffle(players)

        game_log, final_state = play_game(players)
        df = pd.DataFrame(game_log)
        df["game_id"] = f"random_4player_g{game_num}"

        for i in range(4):
            df[f"player_{i}_name"] = labels[i]
            df[f"player_{i}_final"] = final_state.player_money_values[i]

        max_money = max(final_state.player_money_values)
        winners = [labels[i] for i, coins in enumerate(final_state.player_money_values) if coins == max_money]
        df["winners"] = ", ".join(winners)

        logs.append(df)

    pd.concat(logs).to_csv(os.path.join(output_dir, "random_4player_game_logs_pt2.csv"), index=False)

def run_greedy_4player(num_games=100):
    print("Running: greedy_4player")
    logs = []

    for game_num in tqdm(range(num_games), desc="greedy_4player"):
        players = [GreedyAgent] * 4
        labels = ["GreedyAgent"] * 4
        random.shuffle(players)

        game_log, final_state = play_game(players)
        df = pd.DataFrame(game_log)
        df["game_id"] = f"greedy_4player_g{game_num}"

        for i in range(4):
            df[f"player_{i}_name"] = labels[i]
            df[f"player_{i}_final"] = final_state.player_money_values[i]

        max_money = max(final_state.player_money_values)
        winners = [labels[i] for i, coins in enumerate(final_state.player_money_values) if coins == max_money]
        df["winners"] = ", ".join(winners)

        logs.append(df)

    pd.concat(logs).to_csv(os.path.join(output_dir, "greedy_4player_game_logs_pt2.csv"), index=False)

def run_mixed_4player_permutations():
    print("Running: mixed_4player permutations (10x each of 24 permutations)")
    logs = []

    bot_names = ["GreedyAgent", "MCTSAgent", "RoundBetAgent", "GameBetAgent"]
    all_perms = list(permutations(bot_names, 4))
    games_per_perm = 15

    for perm in tqdm(all_perms, desc="mixed_4player"):
        for game_num in range(games_per_perm):
            labels = list(perm)
            players = [bot_classes[name] for name in labels]

            game_log, final_state = play_game(players)
            df = pd.DataFrame(game_log)
            df["game_id"] = f"mixed_4player_{'_'.join(labels)}_{game_num}"

            for i in range(4):
                df[f"player_{i}_name"] = labels[i]
                df[f"player_{i}_final"] = final_state.player_money_values[i]

            max_money = max(final_state.player_money_values)
            winners = [labels[i] for i, coins in enumerate(final_state.player_money_values) if coins == max_money]
            df["winners"] = ", ".join(winners)

            logs.append(df)

    pd.concat(logs).to_csv(os.path.join(output_dir, "mixed_4player_game_logs_pt5555555.csv"), index=False)

def run_fixed_order_4player(num_games=300):
    print("Running: fixed_order_4player (GameBet, MCTS, Greedy, RoundBet)")
    logs = []

    labels = ["GameBetAgent", "MCTSAgent", "GreedyAgent", "RoundBetAgent"]
    players = [bot_classes[name] for name in labels]

    for game_num in tqdm(range(num_games), desc="fixed_order_4player"):
        game_log, final_state = play_game(players)
        df = pd.DataFrame(game_log)
        df["game_id"] = f"fixed_order_4player_g{game_num}"

        for i in range(4):
            df[f"player_{i}_name"] = labels[i]
            df[f"player_{i}_final"] = final_state.player_money_values[i]

        max_money = max(final_state.player_money_values)
        winners = [labels[i] for i, coins in enumerate(final_state.player_money_values) if coins == max_money]
        df["winners"] = ", ".join(winners)

        logs.append(df)

    pd.concat(logs).to_csv(os.path.join(output_dir, "fixed_order_4player_game_logs_pt2.csv"), index=False)
    
def run_mixed_4player_permutations_pt2():
    print("Running: mixed_4player permutations (10x each of 24 permutations)")
    logs = []

    bot_names = ["GreedyAgent", "MCTSAgent", "RollAgent", "RandomAgent"]
    all_perms = list(permutations(bot_names, 4))
    games_per_perm = 10

    for perm in tqdm(all_perms, desc="mixed_4player"):
        for game_num in range(games_per_perm):
            labels = list(perm)
            players = [bot_classes[name] for name in labels]

            game_log, final_state = play_game(players)
            df = pd.DataFrame(game_log)
            df["game_id"] = f"mixed_4player_{'_'.join(labels)}_{game_num}"

            for i in range(4):
                df[f"player_{i}_name"] = labels[i]
                df[f"player_{i}_final"] = final_state.player_money_values[i]

            max_money = max(final_state.player_money_values)
            winners = [labels[i] for i, coins in enumerate(final_state.player_money_values) if coins == max_money]
            df["winners"] = ", ".join(winners)

            logs.append(df)

    pd.concat(logs).to_csv(os.path.join(output_dir, "mixed_4player_game_logs_pt3.csv"), index=False)

def run_roll_and_greedy_fixed_order_4player(num_games=300):
    print("Running: fixed_order_4player (Roll, Greedy, Greedy, Greedy)")
    logs = []

    labels = ["RollAgent", "GreedyAgent", "GreedyAgent", "GreedyAgent"]
    players = [bot_classes[name] for name in labels]

    for game_num in tqdm(range(num_games), desc="fixed_order_4player"):
        game_log, final_state = play_game(players)
        df = pd.DataFrame(game_log)
        df["game_id"] = f"fixed_order_4player_g{game_num}"

        for i in range(4):
            df[f"player_{i}_name"] = labels[i]
            df[f"player_{i}_final"] = final_state.player_money_values[i]

        max_money = max(final_state.player_money_values)
        winners = [labels[i] for i, coins in enumerate(final_state.player_money_values) if coins == max_money]
        df["winners"] = ", ".join(winners)

        logs.append(df)

    pd.concat(logs).to_csv(os.path.join(output_dir, "roll_and_greedy_4player_game_logs_pt2.csv"), index=False)

if __name__ == "__main__":
    # run_random_4player()
    # run_greedy_4player()
    run_mixed_4player_permutations()
    # run_fixed_order_4player()
    # run_mixed_4player_permutations_pt2()
    # run_roll_and_greedy_fixed_order_4player()
    print(f"All game logs saved to: {output_dir}")
