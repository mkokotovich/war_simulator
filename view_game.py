from stats import *
import sys

if len(sys.argv) > 1:
    game_number = int(sys.argv[1])

all_games = Game.select()
if len(all_games) < game_number:
    print "Invalid game number {}, there are only {} games".format(game_number, len(all_games))
    sys.exit(1)
game = all_games[game_number]

status_list = GameStatus.select().where(GameStatus.game == game)

for status in status_list:
    print status.detailed_status()
    #print status

