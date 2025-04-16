import pandas as pd

def analyze_ev_log(log_path="game_logs/GreedyActionEVLog.csv"):
    df = pd.read_csv(log_path)
    df = df[df["action_type"].notna()].copy()

    # Track actual payout (placeholder for now)
    df["payout"] = None

    # Group and compute base EV statistics
    summary = df.groupby("action_type").agg(
        times_chosen=("action_type", "count"),
        avg_ev=("ev", "mean"),
        std_ev=("ev", "std"),
        max_ev=("ev", "max"),
        min_ev=("ev", "min"),
    ).reset_index()

    summary["usage_percent"] = 100 * summary["times_chosen"] / summary["times_chosen"].sum()
    summary["var_ev"] = summary["std_ev"] ** 2

    # Reorder columns
    summary = summary[[
        "action_type", "usage_percent", "times_chosen",
        "avg_ev", "std_ev", "var_ev", "max_ev", "min_ev"
    ]]

    # Manually assign average actual payout values
    avg_payout_lookup = {
        "game_bet": 1.478,
        "move_camel": 1.00,
        "move_trap": 1.4492,
        "round_winner_bet": 1.451
    }

    summary["avg_actual_payout"] = summary["action_type"].map(avg_payout_lookup)

    print(summary)
    return summary


if __name__ == "__main__":
    analyze_ev_log("game_logs/GreedyActionEVLog.csv")
