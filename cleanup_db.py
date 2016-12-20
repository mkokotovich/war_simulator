from stats import *

for game in Game.select():
    if game.total_hands == 0:
        game.delete_instance()
