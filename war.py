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
        hand_aces = 0 if self.hand.size == 0 else len(self.hand.find('Ace'))
        pile_aces = 0 if self.pile.size == 0 else len(self.pile.find('Ace'))
        msg = "Player {} hand: Aces: {}  Total: {}".format(self.name, hand_aces, len(self.hand))
        msg += "\n"
        if debug:
            msg += str(self.hand)
        msg += "Player {} pile: Aces: {}  Total: {}".format(self.name, pile_aces, len(self.pile))
        if debug:
            msg += "\n"
            msg += str(self.pile)
        return msg

    # Returns a single card
    def play_card(self):
        if self.hand.size == 0:
            if self.pile.size == 0:
                # Game over
                return None
            else:
                self.hand += self.pile.empty(return_cards=True)
                self.hand.shuffle()
        return self.hand.deal(1)[0]

    def has_cards(self):
        return self.hand.size != 0 or self.pile.size != 0

    def how_many_cards_can_be_played_for_war(self):
        total_cards = self.hand.size + self.pile.size
        war_cards = 3
        if total_cards < 4:
            war_cards = total_cards - 1
        if total_cards == 0:
            war_cards = 0
        return war_cards

    def add_cards_to_pile(self, cards):
        self.pile += cards

    def __str__(self):
        return self.print_cards(False)


class Trick:
    def __init__(self):
        self.cards = {}
        self.bonus_cards = []
        self.current_winners = {}
        self.current_highest_card = None

    def update_winners_if_needed(self, player_id, card):
        if self.current_highest_card == None or self.current_highest_card.lt(card, POKER_RANKS["values"]):
            self.current_highest_card = card
            self.current_winners = {}
        if self.current_highest_card is not None and self.current_highest_card.eq(card, POKER_RANKS["values"]):
            # Add to winners
            self.current_winners[player_id] = card

    def add_primary_card(self, player_id, card):
        if card is not None:
            self.cards[player_id] = card
            self.update_winners_if_needed(player_id, card)

    def add_bonus_card(self, card):
        if card is not None:
            self.bonus_cards.append(card)

    def is_war(self):
        return len(self.current_winners) > 1

    def prepare_for_war(self):
        self.bonus_cards += self.cards.values()
        self.cards = {}
        self.current_winners = {}
        self.current_highest_card = None

    def get_winner_id(self):
        return self.current_winners.keys()[0]

    def get_all_cards_as_stack(self):
        stack = pydealer.Stack()
        for x in self.cards.values():
            stack += [x]
        for x in self.bonus_cards:
            stack += [x]
        return stack



class WarGameManager:
    def __init__(self, num_players=2):
        self.num_players = num_players
        self.players = {}
        self.deck = pydealer.Deck(ranks=POKER_RANKS)
        self.initialize_players()
        self.number_of_hands = 0

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
        self.number_of_hands = 0
        self.deal_new_deck()

    def is_game_over(self):
        for i in range(0, self.num_players):
            if not self.players[i].has_cards():
                return True
        return False

    def game_summary(self):
        msg = ""
        for i in range(0, self.num_players):
            if self.players[i].has_cards():
                msg +=  "{} won after {} hands".format(self.players[i].name, self.number_of_hands)
                break
        return msg

    def __str__(self):
        msg = ""
        for i in range(0, self.num_players):
            msg += str(self.players[i]) + "\n"
        return msg

    def play_hand(self, debug=False):
        self.number_of_hands += 1
        trick = Trick()
        for i in range(0, self.num_players):
            card = self.players[i].play_card()
            trick.add_primary_card(i, card)
            if debug:
                print "{}: {}".format(self.players[i].name, str(card))
        while trick.is_war():
            trick.prepare_for_war()
            cards_for_war_list = []
            for i in range(0, self.num_players):
                cards_for_war_list.append(self.players[i].how_many_cards_can_be_played_for_war())
            cards_for_war = min(cards_for_war_list)
            if debug:
                print "Warring with {} bonus cards".format(cards_for_war)
            for i in range(0, self.num_players):
                for j in range(0, cards_for_war):
                    card = self.players[i].play_card()
                    trick.add_bonus_card(card)
                    if debug:
                        print "{} added bonus card: {}".format(self.players[i].name, str(card))
                card = self.players[i].play_card()
                trick.add_primary_card(i, card)
                if debug:
                    print "{} war card: {}".format(self.players[i].name, str(card))
        # Give all cards to winner
        cards = trick.get_all_cards_as_stack()
        self.players[trick.get_winner_id()].add_cards_to_pile(cards)
        if debug:
            print "{} won {} cards".format(self.players[trick.get_winner_id()].name, cards.size)


def main():
    war = WarGameManager()
    war.deal_new_deck()
    print war
    while not war.is_game_over():
        war.play_hand(debug=True)
        print war
    print war.game_summary()

if __name__ == "__main__":
    main()
