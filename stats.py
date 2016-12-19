from peewee import *

db = SqliteDatabase('war_stats.db')

class BaseModel(Model):
    class Meta:
        database = db

class Game(BaseModel):
    total_hands = IntegerField()
    winner = CharField()

class WarStats:
    def __init__(self):
        db.connect()
        try:
            db.create_tables([Game])
        except OperationalError:
            # Table already exists
            pass

    def add_game(self, total_hands, winner):
        game = Game(total_hands=total_hands, winner=winner)
        game.save()

    def summarize(self):
        total_games = Game.select().count()
        total_hands = Game.select(fn.SUM(Game.total_hands)).scalar()
        average_hands = total_hands / total_games

        return "{} games have been played, with an average length of {} hands".format(total_games, average_hands)
