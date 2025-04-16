import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from tqdm import tqdm
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

bot_names = list(bot_classes.keys())
games_per_pair = 50
half_games = games_per_pair // 2
log_dir = "tournament_logs"
os.makedirs(log_dir, exist_ok=True)

head_to_head_wins = {bot: {op: 0 for op in bot_names} for bot in bot_names}
player1_wins = {bot: 0 for bot in bot_names}
player2_wins = {bot: 0 for bot in bot_names}
all_games_log = []

total_iterations = len(list(combinations(bot_names, 2))) * games_per_pair

with tqdm(total=total_iterations, desc="Simulating games") as pbar:
    for bot1, bot2 in combinations(bot_names, 2):
        for game_id in range(games_per_pair):
            if game_id < half_games:
                players = [bot_classes[bot1], bot_classes[bot2]]
                player_names = [bot1, bot2]
            else:
                players = [bot_classes[bot2], bot_classes[bot1]]
                player_names = [bot2, bot1]

            game_log, final_state = play_game(players)
            df = pd.DataFrame(game_log)
            df["game_id"] = f"{bot1}_vs_{bot2}_g{game_id}"
            df["bot1"] = bot1
            df["bot2"] = bot2
            df["player_1_name"] = player_names[0]
            df["player_2_name"] = player_names[1]

            coins = final_state.player_money_values
            df["player_1_final"] = coins[0]
            df["player_2_final"] = coins[1]

            if coins[0] > coins[1]:
                winner = player_names[0]
                head_to_head_wins[player_names[0]][player_names[1]] += 1
                player1_wins[player_names[0]] += 1
            elif coins[1] > coins[0]:
                winner = player_names[1]
                head_to_head_wins[player_names[1]][player_names[0]] += 1
                player2_wins[player_names[1]] += 1
            else:
                winner = "tie"
                head_to_head_wins[player_names[0]][player_names[1]] += 0.5
                head_to_head_wins[player_names[1]][player_names[0]] += 0.5
                player1_wins[player_names[0]] += 0.5
                player2_wins[player_names[1]] += 0.5

            df["winner"] = winner
            all_games_log.append(df)

            pbar.update(1)

all_df = pd.concat(all_games_log, ignore_index=True)
all_df.to_csv(os.path.join(log_dir, "all_games_log.csv"), index=False)

win_matrix = pd.DataFrame(head_to_head_wins).T.astype(int)
win_matrix.to_csv(os.path.join(log_dir, "head_to_head_win_matrix.csv"))

pos_win_df = pd.DataFrame({
    "bot": bot_names,
    "wins_as_player_1": [player1_wins[b] for b in bot_names],
    "wins_as_player_2": [player2_wins[b] for b in bot_names],
})
pos_win_df.to_csv(os.path.join(log_dir, "player_position_wins.csv"), index=False)

plt.figure(figsize=(10, 8))
plt.title("Head-to-Head Wins (1v1 Tournament)")
plt.imshow(win_matrix.values, cmap="Blues", interpolation='nearest')
plt.colorbar(label="Wins")
plt.xticks(ticks=np.arange(len(bot_names)), labels=bot_names, rotation=45, ha='right')
plt.yticks(ticks=np.arange(len(bot_names)), labels=bot_names)
for i in range(len(bot_names)):
    for j in range(len(bot_names)):
        plt.text(j, i, str(win_matrix.iloc[i, j]), ha='center', va='center', color='black')
plt.tight_layout()
heatmap_path = os.path.join(log_dir, "head_to_head_heatmap.png")
plt.savefig(heatmap_path)
plt.show()

print("Tournament complete!")
print(f"All game logs saved to: {os.path.join(log_dir, 'all_games_log.csv')}")
print(f"Head-to-head win matrix saved to: {os.path.join(log_dir, 'head_to_head_win_matrix.csv')}")
print(f"Positional win stats saved to: {os.path.join(log_dir, 'player_position_wins.csv')}")
print(f"Heatmap saved to: {heatmap_path}")
