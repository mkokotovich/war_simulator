from peewee import *

db = SqliteDatabase('war_stats.db')

class BaseModel(Model):
    class Meta:
        database = db

class Player(BaseModel):
    name = CharField()

    def __str__(self):
        return str(self.name)


class Game(BaseModel):
    winner = ForeignKeyField(Player, null=True)
    total_hands = IntegerField(null=True)

    def __str__(self):
        return str(self.id)


class GameStatus(BaseModel):
    game = ForeignKeyField(Game)
    player = ForeignKeyField(Player)
    hand = IntegerField()
    total_cards = IntegerField()
    numAce = IntegerField()
    numKing = IntegerField()
    numQueen = IntegerField()
    numJack = IntegerField()
    num10 = IntegerField()
    num9 = IntegerField()
    num8 = IntegerField()
    num7 = IntegerField()
    num6 = IntegerField()
    num5 = IntegerField()
    num4 = IntegerField()
    num3 = IntegerField()
    num2 = IntegerField()

    card_attributes = [
        "numAce",
        "numKing",
        "numQueen",
        "numJack",
        "num10",
        "num9",
        "num8",
        "num7",
        "num6",
        "num5",
        "num4",
        "num3",
        "num2"
    ]

    def __str__(self):
        return "Game: {} Player: {} Hand: {} Total: {}".format(self.game, self.player, self.hand, self.total_cards)

    def detailed_status(self):
        return "Game: {} Player: {} Hand: {} Total: {} A:{} K:{} Q:{} J:{} 10:{} 9:{} 8:{} 7:{} 6:{} 5:{} 4:{} 3:{} 2:{}".format(
                self.game, self.player, self.hand, self.total_cards, self.numAce, self.numKing, self.numQueen, self.numJack,
                self.num10, self.num9, self.num8, self.num7, self.num6, self.num5, self.num4, self.num3, self.num2)


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

    def add_game_status(self, current_hand, player, card_count_dict, total_cards):
        if player not in self.player_cache:
            player_id, created = Player.get_or_create(name=player)
            self.player_cache[player] = player_id
            if created:
                player_id.save()
        status_entry = {
                 'game': self.current_game,
                 'hand': current_hand,
                 'player': self.player_cache[player],
                 'total_cards': total_cards
             }
        for key, value in list(card_count_dict.items()):
            status_entry["num{}".format(key)] = value
        self.status_cache.append(status_entry)

    def finalize_game(self, total_hands, winner):
        with db.atomic():
            for idx in range(0, len(self.status_cache), 1000):
                GameStatus.insert_many(self.status_cache[idx:idx+1000]).execute()
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

        for player in Player.select():
            games_won = Game.select().where(Game.winner == player.id).count()
            print(f"Player {player} won {games_won} games")

        number_of_hands_after_four_cards = {}
        number_of_hands_won_by_first_to_four_cards = {}
        for attr in GameStatus.card_attributes:
            number_of_hands_after_four_cards[attr] = []
            number_of_hands_won_by_first_to_four_cards[attr] = 0

        for game in Game.select():
            for attr in GameStatus.card_attributes:
                query=GameStatus.select().join(Game).where(Game.id==game).where(getattr(GameStatus, attr) == 4).order_by(GameStatus.hand)
                first_to_four_cards = query[0].player 
                hand_with_first_four_cards = query[0].hand
                if first_to_four_cards == game.winner:
                    number_of_hands_won_by_first_to_four_cards[attr] += 1
                number_of_hands_after_four_cards[attr].append(game.total_hands - hand_with_first_four_cards)
        first_four_card_winning_percentage = {}
        for attr in GameStatus.card_attributes:
            first_four_card_winning_percentage[attr] = 100*number_of_hands_won_by_first_to_four_cards[attr]/float(total_games)
        msg += "Player to reach four of these cards first won the following percent of the time:\n"
        for attr in GameStatus.card_attributes:
            msg += "{}: {:.1f} ".format(attr, first_four_card_winning_percentage[attr])
        msg += "\n"
        msg += "Average number of hands remaining after first person reaches four of these cards:\n"
        for attr in GameStatus.card_attributes:
            msg += "{}: {:.1f} ".format(attr, sum(number_of_hands_after_four_cards[attr])/float(total_games))
        msg += "\n"
        return msg


def main():
    stats = WarStats()
    print(stats.summarize())

if __name__ == "__main__":
    main()

