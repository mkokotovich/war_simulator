from stats import *

def run_query():
    msg = ""
    number_of_cards_at_four_cards = {}
    for attr in GameStatus.card_attributes:
        number_of_cards_at_four_cards[attr] = []

    for game in Game.select():
        for attr in GameStatus.card_attributes:
            query=GameStatus.select().join(Game).where(Game.id==game).where(getattr(GameStatus, attr) == 4).order_by(GameStatus.hand)
            number_of_cards_at_four_cards[attr].append(query[0].total_cards)
    msg += "Average number of cards needed when first getting all four of this card,\n"
    for attr in GameStatus.card_attributes:
        msg += "{},{:.1f}\n".format(attr[3:], sum(number_of_cards_at_four_cards[attr])/float(len(number_of_cards_at_four_cards[attr])))
    msg += "\n"
    return msg

def main():
    print(run_query())

if __name__ == "__main__":
    main()

