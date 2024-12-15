class PlayerInterface:
    """
    All bots must extend this interface and implement the method 'move()'.

    This function should return one of the following tuples
        - (MOVE_CAMEL_ACTION_ID, )                            Roll the dice and randomly move a camel
        - (MOVE_TRAP_ACTION_ID, trap_type, trap_location)     Move trap to a given location.
                                                                    - trap_type: +1/-1 depending on whether
                                                                      it adds or removes one from the roll
                                                                    - trap_location: ranges from 0 to board_size
                                                                      (exclusive)
        - (ROUND_BET_ACTION_ID, camel_id)                     Make round winner bet
                                                                    - camel_id: Camel ID
        - (GAME_BET_ACTION_ID, bet_type, camel_id)            Make game winner or loser bet
                                                                    - bet_type: "win"/"lose" for winner/loser bet,
                                                                      respectively
                                                                    - camel_id: Camel ID

    See the file actionids.py for more details on the action IDs.

    Note that the game independently checks that moves are permissible but will raise exceptions if they are not. Your
    subclass must ensure that only valid movies are made. That means your code must check that:
    - traps should only be placed on valid squares
    - round winner bets on a camel can only be made if there are still betting
      cards available
    - game winner and loser bets on a camel can only be made once by each player

    The recommended method of selecting a move is to use the camelup.get_valid_moves() function, which returns a list
    of tuples describing all legal moves for the given player. The game engine will check that the move submitted by
    a bot is on this list.

    Subclasses should remain stateless and the move()-function should be a static function as the game-code never
    instantiates any of the player classes.
    """
    @staticmethod
    def move(active_player, game_state):
        raise NotImplementedError(
            "Do not create an instance of the PlayerInterface! "
            "Extend this class and make sure to implement the move() function.")

# class Player1(PlayerInterface):
#     def move(self, g):
#         # This player is less dumb. If they have the least amount of money they'll make a round winner bet
#         # If they aren't in last then they'll place a trap on a random square. Still p dumb though
#         if min(g.player_money_values) == g.player_money_values[player]:
#             return [2,random.randint(0,len(g.camels)-1)]
#         return [1,math.floor(2*random.random())*2-1,random.randint(1,10)]

# class Player2(PlayerInterface):
#     def move(player,g):
#         #This dumb player always makes a round winner bet
#         return [2,random.randint(0,len(g.camels)-1)]
