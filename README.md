# CamelAI
A data-driven approach to decision-making in the context of camel race betting

## Introduction
This project aims to understand the decision-making process in a competitive market with limited resources. The proxy for this scenario is the game [Camel Up](https://en.wikipedia.org/wiki/Camel_Up) by Pegasus Spiele. The core mechanics of the game involve placing bets on camels on a race track. The game is divided into 'rounds', in which each of the camels are moved in a random order. Players can choose one of four actions each turn:

- move a random camel along the track,
- place traps to impede or help camels that land on them,
- make a bet on which camel will be furthest along at the end of the current round, or
- make a bet on which camel will win or lose the entire game.

The game's difficult stems from the fact that camels can stack on top of each other if they land on the same space. If a camel is moved, all camels on top of it in the stack are also moved. This adds a layer of complexity to the game that makes it nearly impossible for a human player to fully understand the joint probability of any action being "good" in the sense that it optimizes the player's probability of winning.

This project consists of several elements that will be used to analyze the game mechanics and the joint probabilities of any given action increasing the win-rate of a player.

## Simulating the game
The basis of this project is a digital version of Camel Up that allows the simulation of a game. This digital game consists of three elements:
1. Game engine: keeps track of player actions and the current game state,
2. Rules engine: determines which actions are permissible and which are forbidden based on the current game state,
3. Player bots: decide, on the basis of the current game state, which actions to execute.

![Game Flowchart](images/GameEngineFlowChart.png)

Upon a player's turn, the player bot receives the current game state as well as a list of all valid action. On this basis, it chooses an action to perform and communicates this to the game engine. The game engine ensures that this action is valid and then updates the game state accordingly.

The easiest way to simulate a game is by running the following shell command from the command line:

```bash
python rungame.py <NUM_GAMES> <PLAYER_1> ... <PLAYER_N>
```

where NUM_GAMES is an integer indicating how many games should be simulated. PLAYER_1, ..., PLAYER_N are the names of the player bots to set as players. These should be the names of classes in the `bots.py` file. See below for more information on the bots.

The command `python rungame.py 100 RandomBot RandomBot RandomBot RandomBot` would therefore simulate 100 games between four identical players (`RandomBot`) whose strategy is to select a random action.

The game logs are stored as CSV files in the directory `game_logs`. See below for more information on the logs

## Player Bots
Player bots are technically simple. They are simply custom Python classes that extend the PlayerInterface class. They require only a single method, `move()`, which communicates to the game engine what action to take. The permitted actions must be one of:

| Action | Description |
| ------ | ----------- |
| `(0, )`  | Move a camel |
| `(1, trap_type, trap_location)` | Place a trap |
| `(2, camel_id)` | Make a bet on the round winner |
| `(3, bet_type, camel_id)` | Make a bet on the game winner or loser |

To ensure error-free execution, it is advised to use the `get_valid_moves()` function to obtain a list of permissible actions. For an example on how to create a custom player bot, see the abstract superclass `playerinterface.PlayerInterface` as well as `bots.RandomBot`, which randomly selects an action to perform.

Player bots can see the current game state as well as all permitted rules. However, they only get semi-anonymized game winner/loser bets as these are secret as per game rules. Stay tuned for more detailed instructions on how to interact with the game state and create a custom player bot.

## Game Logs
Game logs are output as CSV files in the `game_logs` directory. Each row represents a game round and contains information on the player action as well as the resulting game state, e.g. row N would show what action was taken and by whom in round N and a summary of the resulting game state at the end of round N.

The first row of the game log describes the starting conditions before any actions are performed.

Currently, the following columns are (in alphabetical order):

| Column | Description |
| ------ | ----------- |
| active_player | The player who performed an action during this round |
| bet_type | If the player made a game bet, was it a bet on the winner or loser? |
| camel | What camel was moved or bet on |
| camel\_<CAMEL_NAME>\_location | The current location of camel with the name <CAMEL_NAME> on the board (these will usually be c_1 to c_M by default) |
| camel\_<CAMEL_NAME>\_stack_location | The current location of camel with the name <CAMEL_NAME> within the stack. The bottom-most camel will have the stack location 0 and the leading camel of the stack will have the highest stack location. No two camels should ever have the same board and stack location |
| distance | How far was the camel moved? This is the net distance, i.e. if the camel landed on a trap then this is taken into consideration |
| player\_#\_coins | How many coins a player has |
| player\_#\_trap_location | Where the player's trap is on the board |
| player\_#\_trap_type | Whether the player has set his trap to +/- |
| round_id | The number of the current round (one player action constitutes a round) |
| trap_location | Where a player placed his trap if he placed it in this turn (this is technically redundant with player\_#\_trap_location) |
| trap_type | Whether a player placed a +/- trap if he placed it in this turn (this is technically redundant with player\_#\_trap_type) |
