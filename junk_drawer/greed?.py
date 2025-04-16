import os
import pandas as pd
from tqdm import tqdm
from camelup import play_game, find_camel_in_nth_place, summarize_game_state
from bots import GreedyAgent
from actionids import *
import matplotlib.pyplot as plt

output_dir = "action_logs"
os.makedirs(output_dir, exist_ok=True)

def detect_actual_rounds(game_df):
    rounds = []
    current_round = 1
    roll_count = 0
    for _, row in game_df.iterrows():
        if row.get("action_type") == "move_camel":
            roll_count += 1
            if roll_count == 5:
                current_round += 1
                roll_count = 0
        rounds.append(current_round)
    return rounds

def get_camel_placements(row):
    positions = []
    for i in range(5):
        camel = f"c_{i}"
        pos = row[f"camel_{camel}_location"]
        stack = row[f"camel_{camel}_stack_location"]
        positions.append((camel, pos, stack))
    placements = sorted(positions, key=lambda x: (-x[1], -x[2]))
    return [camel for camel, _, _ in placements]

def analyze_greedy_games(num_games=100):
    action_logs = []

    for game_id in tqdm(range(num_games), desc="Simulating Greedy Games"):
        game_log, final_state = play_game([GreedyAgent] * 4)
        df = pd.DataFrame(game_log)
        df.to_csv(os.path.join(output_dir, f"game_log_{game_id}.csv"), index=False)
        df["game_id"] = game_id

        actual_rounds = detect_actual_rounds(df)
        df["actual_round"] = actual_rounds

        round_end_states = {}
        for i in range(1, len(df)):
            prev_round = df.iloc[i-1]["actual_round"]
            curr_round = df.iloc[i]["actual_round"]
            if curr_round > prev_round:
                round_end_states[prev_round] = df.iloc[i]

        final_coins = final_state.player_money_values
        winning_coins = max(final_coins)
        final_placements = get_camel_placements(summarize_game_state(final_state))
        print(final_placements)

        placed_traps = {}  # (player_id, trap_location) -> (turn index, round number)
        round_bets = []    # accumulate to score later by round

        for i, row in df.iterrows():
            if "action_type" not in row or pd.isna(row["active_player"]):
                continue

            player = int(row["active_player"])
            action_type = row["action_type"]
            before_coins = df.iloc[i - 1][f"player_{player}_coins"] if i > 0 else 2
            after_coins = row.get(f"player_{player}_coins", before_coins)

            entry = {
                "game_id": game_id,
                "turn_id": row["round_id"],
                "round_number": row["actual_round"],
                "player_id": player,
                "action_type": action_type,
                "coin_before": before_coins,
                "coin_after": after_coins,
                "coin_delta": after_coins - before_coins,
                "player_final_coins": final_coins[player],
                "player_won_game": final_coins[player] == winning_coins,
                "payout": 0
            }

            if action_type == "round_winner_bet":
                camel = row.get("camel")
                entry["camel"] = camel
                round_num = row["actual_round"]
                round_bets.append((round_num, camel, player, len(round_bets), entry))

            elif action_type == "game_bet":
                camel = row.get("camel")
                bet_type = row.get("bet_type")
                entry["camel"] = camel
                entry["bet_type"] = bet_type
                entry["game_bet_key"] = (bet_type, camel)
                entry["payout"] = -1

            elif action_type == "move_trap":
                trap_loc = row.get("trap_location")
                entry["trap_type"] = row.get("trap_type")
                entry["trap_location"] = trap_loc
                placed_traps[(player, trap_loc)] = (i, row["actual_round"])

            elif action_type == "move_camel":
                entry["camel"] = row.get("camel")
                entry["distance"] = row.get("distance")

            action_logs.append(entry)

        # Score round bets
        bet_counters = {}
        for round_num, camel, player, idx, entry in round_bets:
            state_row = round_end_states.get(round_num, df.iloc[-1])
            placements = get_camel_placements(state_row)
            if camel not in placements:
                entry["payout"] = 0
                continue
            bet_index = bet_counters.get((round_num, camel), 0)
            bet_counters[(round_num, camel)] = bet_index + 1
            if placements[0] == camel:
                entry["payout"] = [5, 3, 2][bet_index] if bet_index < 3 else 2
            elif placements[1] == camel:
                entry["payout"] = [1, 1, 1][bet_index] if bet_index < 3 else 1
            else:
                entry["payout"] = -1

        # Score trap payouts using total round delta - known payouts
        df_actions = pd.DataFrame(action_logs)

        # Ensure move_camel always has payout = 1
        df_actions.loc[df_actions["action_type"] == "move_camel", "payout"] = 1

        # Score game bets with correct ordering
        game_bet_df = df_actions[df_actions["action_type"] == "game_bet"]
        for (bet_type, camel), group in game_bet_df.groupby(["bet_type", "camel"]):
            correct_place = (0 if bet_type == "win" else 4)  # win -> 1st, lose -> last
            if camel in final_placements and \
               ((bet_type == "win" and final_placements.index(camel) == correct_place) or
                (bet_type == "lose" and final_placements.index(camel) == correct_place)):
                for j, (_, row) in enumerate(group.iterrows()):
                    payout = [8, 5, 3, 2][j] if j < 4 else 2
                    df_actions.at[row.name, "payout"] = payout
            else:
                for _, row in group.iterrows():
                    df_actions.at[row.name, "payout"] = -1
        
        # Score trap payouts using total round delta - known payouts
        for (player, loc), (idx, round_num) in placed_traps.items():
            this_round_actions = df_actions[
                (df_actions["round_number"] == round_num) & (df_actions["player_id"] == player)
            ]
            total_delta = this_round_actions["coin_delta"].sum()
            known_payout = this_round_actions[
                this_round_actions["action_type"].isin(["round_winner_bet", "game_bet"])
            ]["payout"].sum()
            print("total " + str(total_delta))
            print("knwon " + str(known_payout))
            # print("total+known " + str(total_delta - known_payout))
            df_actions.at[idx, "payout"] = max(0, total_delta - known_payout)

        df_actions.to_csv(os.path.join(output_dir, "greedy_action_log.csv"), index=False)

        summary = df_actions.groupby("action_type").agg(
            num_uses=("action_type", "count"),
            avg_delta=("coin_delta", "mean"),
            avg_payout=("payout", "mean"),
            win_rate=("player_won_game", "mean")
        ).reset_index()
        summary.to_csv(os.path.join(output_dir, "action_summary.csv"), index=False)

        plt.figure(figsize=(10, 5))
        plt.bar(summary["action_type"], summary["avg_delta"])
        plt.title("Average Coins Gained per Action Type")
        plt.ylabel("Avg Coins")
        plt.savefig(os.path.join(output_dir, "avg_coin_gain_per_action.png"))
        plt.close()

        plt.figure(figsize=(10, 5))
        plt.bar(summary["action_type"], summary["num_uses"])
        plt.title("Frequency of Each Action Type")
        plt.ylabel("Count")
        plt.savefig(os.path.join(output_dir, "action_frequency.png"))
        plt.close()

        print("Analysis complete! Logs and stats saved to:", output_dir)

if __name__ == "__main__":
    analyze_greedy_games(1)
