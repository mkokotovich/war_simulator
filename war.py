# Simulator for the card game war

import pydealer
from pydealer.const import POKER_RANKS
from random import randint

class Player:
    def __init__(self, initial_cards=None, name=None):
        self.hand = pydealer.Stack()
        self.pile = pydealer.Stack()
        if initial_cards:
            self.hand += initial_cards
        if name:
            self.name = name
        else:
            self.name = "player{}".format(randint(0,100))

    def set_initial_cards(self, initial_cards):
        self.hand = pydealer.Stack()
        self.hand += initial_cards

    def print_cards(self, debug=False):
        msg = "Player {} hand: Aces: {}  Total: {}".format(self.name, len(self.hand.find('Ace')), len(self.hand))
        msg += "\n"
        if debug:
            msg += str(self.hand)
        msg += "Player {} pile: Aces: {}  Total: {}".format(self.name, len(self.pile.find('Ace')), len(self.pile))
        if debug:
            msg += "\n"
            msg += str(self.pile)
        return msg

    # Returns a single card
    def play_card(self):
        if len(self.hand.cards) == 0:
            if len(self.pile.cards) == 0:
                # Game over
                return None
            else:
                self.hand += self.pile.empty(return_cards=True)
                self.hand.shuffle()
        return self.hand.deal(1)[0]

    def still_playing(self):
        # Work around bug in pydealer where size() on empty Stack fails
        return len(self.hand.cards) != 0 or len(self.pile.cards) != 0

    def add_cards_to_pile(self, cards):
        self.pile += cards

    def __str__(self):
        return self.print_cards(False)


class WarGameManager:
    def __init__(self, num_players=2):
        self.num_players = num_players
        self.players = {}
        self.deck = pydealer.Deck(ranks=POKER_RANKS)
        self.initialize_players()

    def initialize_players(self):
        for i in range(0, self.num_players):
            self.players[i] = Player()

    def deal_new_deck(self):
        self.deck = pydealer.Deck()
        self.deck.shuffle()
        for i in range(0, self.num_players):
            self.players[i].set_initial_cards(self.deck.deal(26))

    def reset_game(self):
        self.initialize_players()
        self.deal_new_deck()

    def is_game_over(self):
        for i in range(0, self.num_players):
            if not self.players[i].still_playing():
                return True
        return False


    def __str__(self):
        msg = ""
        for i in range(0, self.num_players):
            msg += str(self.players[i]) + "\n"
        return msg

    def play_hand(self, debug=False):
        hand = {}
        for i in range(0, self.num_players):
            hand[i] = self.players[i].play_card()
            if debug:
                print "{}: {}".format(self.players[i].name, str(hand[i]))
        winning_card = max(hand.values())
        winners = {}
        for i in range(0, self.num_players):
            if hand[i] == winning_card:
                winners[i] = winning_card
        if len(winners) == 1:
            # One winner, no war
            winner_id = winners.keys()[0]
            cards = pydealer.Stack()
            for x in hand.values():
                cards += [x]
            self.players[winner_id].add_cards_to_pile(cards)
        else:
            # WAR
            # TODO: make war logic
            winner_id = winners.keys()[0]
            self.players[winner_id].add_cards_to_pile(list(hand.values()))


def main():
    war = WarGameManager()
    war.deal_new_deck()
    print war
    while not war.is_game_over():
        war.play_hand(debug=True)
        print war

if __name__ == "__main__":
    main()
