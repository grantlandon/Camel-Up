import pandas as pd
import os
import sys
import camelup
import bots
import tqdm


def run_game(num_games, players, log_file_path="GameLogs.csv"):
    """
    Simulate Camel Up games with the given list of player bots and write logs directly into a single file.
    :param num_games: An integer, number of games to simulate.
    :param players: A list of classes inheriting PlayerInterface.
    :param log_file_path: The path to the output log file.
    """
    # Initialize an empty list to hold data for all games
    all_games_data = []

    for i in range(num_games):
        print("Simulating game {} out of {}".format(i + 1, num_games))
        
        # Play the game
        game, gamestate = camelup.play_game(players=players)
        game = pd.DataFrame(game)
        game["game_id"] = i  # Add a game_id column
        
        # Append game data to the list
        all_games_data.append(game)

    # Concatenate all games' data into a single DataFrame
    combined_data = pd.concat(all_games_data, sort=True).reset_index(drop=True)

    # Sort the data by game_id and round_id for consistency
    combined_data = combined_data.sort_values(["game_id", "round_id"])

    # Reorder columns to match the expected format
    first_columns = ["game_id", "round_id"]
    remaining_columns = [col for col in combined_data.columns if col not in first_columns]
    combined_data = combined_data[first_columns + remaining_columns]

    # Write the combined data to the specified log file
    combined_data.to_csv(log_file_path, header=True, index=False)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python {} <NUM_GAMES> <PLAYER_1> ... <PLAYER_N>\n".format(sys.argv[0]) +
            "PLAYER_J should be the name of a bot class to be imported from bots.py\n" +
            "The game can technically run with a single player")
        exit(0)

    # Parse the number of games
    try:
        num_games = int(sys.argv[1])
    except ValueError:
        print("NUM_GAMES must be an integer")
        exit(1)

    # Parse the player bots
    player_bots = []
    for bot_name in sys.argv[2:]:
        player_bots.append(getattr(bots, bot_name))

    print("Simulating {} games with {} players: {}...".format(num_games, len(player_bots), str(player_bots)))

    # Ensure the directory exists for the log file
    os.makedirs("game_logs", exist_ok=True)
    
    # Define the output log file path
    log_file_path = os.path.join("game_logs", "GameLogs.csv")
    
    # Run the game simulation
    run_game(num_games=num_games, players=player_bots, log_file_path=log_file_path)
