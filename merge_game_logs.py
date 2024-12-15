import pandas as pd
import os
import sys
import re

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python {} <DIRECTORY>".format(sys.argv[0]))
        exit(0)

    logdir = sys.argv[1]

    files = [
        f for f in os.listdir(logdir) if
        re.match("game_[0-9]+\.csv", f) is not None]

    print("Merging {} game logs ...".format(len(files)))

    games = []
    for file in files:
        i = int(re.match(r"game_([0-9]+)\.csv", file).groups()[0])
        dat = pd.read_csv(os.path.join(logdir, file), index_col=0)
        dat["game_id"] = i
        games.append(dat)
    games = pd.concat(games, sort=True)
    games = games.sort_values(["game_id", "round_id"])

    first_columns = ["game_id", "round_id"]
    remaining_columns = [col for col in games.columns if col not in first_columns]
    games = games[first_columns + remaining_columns]
    games.to_csv("game_logs/GameLogs.csv", header=True, index=False)
