# Action IDs are here to avoid "magic numbers" in the code that may become inconsistent.
# They can hypothetically be changed but this will have no impact on the program logic.
#
# PlayerInterface objects should use these variable names rather than the actual values when passing instructions to
# the game engine to ensure backwards compatibility if the game engine code is updated.
#
# Note that this doesn't mean these should be changed. In fact, unless there is a REALLY good reason to, don't. The
# test cases hard-code these values to make sure that you think long and hard about why you're changing them.
MOVE_CAMEL_ACTION_ID = 0
MOVE_TRAP_ACTION_ID = 1
ROUND_BET_ACTION_ID = 2
GAME_BET_ACTION_ID = 3
