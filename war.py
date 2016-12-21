# Simulator for the card game war

import pydealer
import sys
from pydealer.const import POKER_RANKS
from random import randint
from stats import WarStats

class CardCount:
    def __init__(self):
        self.counts = {
            "Ace": 0,
            "King": 0,
            "Queen": 0,
            "Jack": 0,
            "10": 0,
            "9": 0,
            "8": 0,
            "7": 0,
            "6": 0,
            "5": 0,
            "4": 0,
            "3": 0,
            "2": 0,
        }

    def add_card(self, card):
        self.counts[card.value] += 1

    def remove_card(self, card):
        self.counts[card.value] -= 1

    def get_count(self, card_str):
        return self.counts[card_str]

    def get_total(self):
        return sum(self.counts.values())

    def get_count_dict(self):
        return self.counts


class Player:
    def __init__(self, player_id, initial_cards=None):
        self.hand = pydealer.Stack()
        self.pile = pydealer.Stack()
        self.card_count = CardCount()
        if initial_cards:
            self.hand += initial_cards
            for card in initial_cards:
                self.card_count.add_card(card)
        self.name = "player{}".format(player_id)

    def set_initial_cards(self, initial_cards):
        self.hand = pydealer.Stack()
        self.hand += initial_cards
        for card in initial_cards:
            self.card_count.add_card(card)

    def get_card_count(self):
        return self.card_count.get_count_dict()

    def number_of_cards(self):
        return self.card_count.get_total()

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
        card_to_play = self.hand.deal(1)[0]
        self.card_count.remove_card(card_to_play)
        return card_to_play

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
        for card in cards:
            self.card_count.add_card(card)

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
            self.players[i] = Player(i)

    def deal_new_deck(self):
        self.deck = pydealer.Deck(ranks=POKER_RANKS)
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

    def get_winner(self):
        for i in range(0, self.num_players):
            if self.players[i].has_cards():
                return self.players[i].name

    def get_players(self):
        return self.players.values()

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


class WarSimulator:
    def __init__(self, debug=False):
        self.debug = debug
        self.war = WarGameManager()
        self.war_stats = WarStats()

    def play_game(self):
        self.war.reset_game()
        self.war_stats.add_new_game()
        for player in self.war.get_players():
            self.war_stats.add_game_status(self.war.number_of_hands, player.name, player.get_card_count(), player.number_of_cards())
        while not self.war.is_game_over():
            self.war.play_hand(self.debug)
            for player in self.war.get_players():
                self.war_stats.add_game_status(self.war.number_of_hands, player.name, player.get_card_count(), player.number_of_cards())
            if self.debug:
                print self.war
        if self.debug:
            print self.war.game_summary()
        self.war_stats.finalize_game(self.war.number_of_hands, self.war.get_winner())

    def run(self, num_games=1):
        sys.stdout.write("Running simulation")
        for n in range(0, num_games):
            sys.stdout.write(".")
            sys.stdout.flush()
            self.play_game()
        sys.stdout.write("\n")

    def stats(self):
        return self.war_stats.summarize()

def main():
    num_runs = 20
    print "Setting up..."
    sim = WarSimulator(debug=False)
    if len(sys.argv) > 1:
        num_runs = int(sys.argv[1])
    sim.run(num_runs)
    print "Generating stats..."
    print sim.stats()

if __name__ == "__main__":
    main()
