from peewee import *

db = SqliteDatabase('war_stats.db')

class BaseModel(Model):
    class Meta:
        database = db

class Player(BaseModel):
    name = CharField()

class Game(BaseModel):
    winner = ForeignKeyField(Player)
    total_hands = IntegerField()

class WarStats:
    def __init__(self):
        db.connect()
        db.create_tables([Game, Player], safe=True)

    def add_game(self, total_hands, winner):
        player, created = Player.get_or_create(name=winner)
        game = Game(total_hands=total_hands, winner=player)
        game.save()
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
        return msg
