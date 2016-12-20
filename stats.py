from peewee import *

db = SqliteDatabase('war_stats.db')

class BaseModel(Model):
    class Meta:
        database = db

class Player(BaseModel):
    name = CharField()

class Game(BaseModel):
    winner = ForeignKeyField(Player, null=True)
    total_hands = IntegerField(null=True)

class GameStatus(BaseModel):
    game = ForeignKeyField(Game)
    player = ForeignKeyField(Player)
    hand = IntegerField()
    aces = IntegerField()
    total_cards = IntegerField()
    def __str__(self):
        return "Game: {} Player: {} Hand: {} Aces: {} Total: {}".format(self.game, self.player, self.hand, self.aces, self.total_cards)

class WarStats:
    def __init__(self):
        db.connect()
        db.create_tables([Game, Player, GameStatus], safe=True)
        self.current_game = None
        self.player_cache = {}
        self.status_cache = []

    def reset(self):
        self.current_game = None
        self.player_cache = {}
        self.status_cache = []

    def add_new_game(self):
        self.reset()
        game = Game(winner=None, total_hands=0)
        game.save()
        self.current_game = game

    def add_game_status(self, current_hand, player, aces, total_cards):
        if player not in self.player_cache:
            player_id, created = Player.get_or_create(name=player)
            self.player_cache[player] = player_id
            if created:
                player_id.save()
        self.status_cache.append(
                {'game': self.current_game,
                 'hand': current_hand,
                 'player': self.player_cache[player],
                 'aces': aces,
                 'total_cards': total_cards})

    def finalize_game(self, total_hands, winner):
        with db.atomic():
            for idx in range(0, len(self.status_cache), 100):
                GameStatus.insert_many(self.status_cache[idx:idx+100]).execute()
        self.current_game.total_hands=total_hands
        player, created = Player.get_or_create(name=winner)
        self.current_game.winner=player
        self.current_game.save()
        if created:
            player.save()

    def summarize(self):
        msg = ""
        total_games = Game.select().count()
        total_hands = Game.select(fn.SUM(Game.total_hands)).scalar()
        average_hands = total_hands / total_games
        msg += "{} games have been played, with an average length of {} hands\n".format(total_games, average_hands)
        subq = Game.select(fn.COUNT(Game.id)).where(Game.winner == Player.id)
        query = (Player.select(Player, Game, subq.alias("games_won")).join(Game, JOIN.LEFT_OUTER).order_by(Player.name))
        for player in query.aggregate_rows():
            msg += "{} has won {} games\n".format(player.name, player.games_won)
        number_of_hands_after_four = []
        number_of_hands_won_by_first_to_four = 0
        for game in Game.select():
            query=GameStatus.select().join(Game).where(Game.id==game).where(GameStatus.aces == 4).order_by(GameStatus.hand)
            first_to_four = query[0].player 
            hand_with_first_four = query[0].hand
            if first_to_four == game.winner:
                number_of_hands_won_by_first_to_four += 1
            number_of_hands_after_four.append(game.total_hands - hand_with_first_four)
        first_four_ace_winning_percentage = 100*number_of_hands_won_by_first_to_four/float(total_games)
        msg += "Player to reach four aces first won {} percent of the time\n".format(first_four_ace_winning_percentage)
        msg += "Average number of hands remaining after first person reaches four aces: {}".format(sum(number_of_hands_after_four)/float(total_games))
        return msg

def main():
    stats = WarStats()
    print stats.summarize()

if __name__ == "__main__":
    main()

