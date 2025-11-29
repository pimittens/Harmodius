import random
from enum import Enum
from itertools import combinations


# spades are congruent to 0 (mod 4), hearts to 1, diamonds to 2, clubs to 3
# value of the card is num // 4 + 1, except for face cards and joker
class Card(Enum):
    AceOfSpades = 0
    AceOfHearts = 1
    AceOfDiamonds = 2
    AceOfClubs = 3
    TwoOfSpades = 4
    TwoOfHearts = 5
    TwoOfDiamonds = 6
    TwoOfClubs = 7
    ThreeOfSpades = 8
    ThreeOfHearts = 9
    ThreeOfDiamonds = 10
    ThreeOfClubs = 11
    FourOfSpades = 12
    FourOfHearts = 13
    FourOfDiamonds = 14
    FourOfClubs = 15
    FiveOfSpades = 16
    FiveOfHearts = 17
    FiveOfDiamonds = 18
    FiveOfClubs = 19
    SixOfSpades = 20
    SixOfHearts = 21
    SixOfDiamonds = 22
    SixOfClubs = 23
    SevenOfSpades = 24
    SevenOfHearts = 25
    SevenOfDiamonds = 26
    SevenOfClubs = 27
    EightOfSpades = 28
    EightOfHearts = 29
    EightOfDiamonds = 30
    EightOfClubs = 31
    NineOfSpades = 32
    NineOfHearts = 33
    NineOfDiamonds = 34
    NineOfClubs = 35
    TenOfSpades = 36
    TenOfHearts = 37
    TenOfDiamonds = 38
    TenOfClubs = 39
    JackOfSpades = 40
    JackOfHearts = 41
    JackOfDiamonds = 42
    JackOfClubs = 43
    QueenOfSpades = 44
    QueenOfHearts = 45
    QueenOfDiamonds = 46
    QueenOfClubs = 47
    KingOfSpades = 48
    KingOfHearts = 49
    KingOfDiamonds = 50
    KingOfClubs = 51
    Joker = 52


class Suit(Enum):
    Spades = 0
    Hearts = 1
    Diamonds = 2
    Clubs = 3
    JokerSuit = 4


class Phase(Enum):
    Attack = 0
    Discard = 1
    JokerChoosePlayer = 2


def get_suit(card):
    if card.value == 52:
        return Suit.JokerSuit
    return Suit(card.value % 4)


def get_value(card):
    if card.value == 52:
        return 0  # joker
    if card.value > 47:
        return 20  # king
    if card.value > 43:
        return 15  # queen
    if card.value > 39:
        return 10  # jack
    return card.value // 4 + 1


class FastGame:
    def __init__(self, num_players):
        self.max_hand_size = 9 - num_players
        self.hands = tuple([[] for _ in range(num_players)])
        self.castle = self.create_castle_deck()
        self.tavern = self.create_tavern_deck()
        self.discard = []
        self.played_cards = []
        self.round_played_cards = []
        self.defense = 0
        self.joker_used = False
        self.active_player = 0
        self.enemy = self.castle.pop()
        self.enemy_hp = 20
        self.yields = 0
        self.won = False
        self.lost = False
        self.phase = Phase.Attack
        self.available_jokers = 2  # only used in single player
        self.deal_starting_hands()

    def clone_state(self):
        # todo
        pass

    def render_state(self):
        print(f"active player: {self.active_player}, phase: {self.phase.name}")
        for i in range(len(self.hands)):
            print(f"player {i}'s hand:")
            for card in self.hands[i]:
                print(card.name)
        print(f"current enemy: {self.enemy.name}, hp: {self.enemy_hp}, disabled: {self.joker_used}")
        print("played cards:")
        for card in self.played_cards:
            print(card.name)
        print(f"defense: {self.defense}")
        print(f"cards in tavern: {len(self.tavern)}")
        print(f"discard pile ({len(self.discard)} cards):")
        for card in self.discard:
            print(card.name)

    def make_move(self, move):
        match self.phase:
            case Phase.Attack:
                if move:
                    self.yields = 0
                    for card in move:
                        self.hands[self.active_player].remove(card)
                        self.played_cards.append(card)
                    total = 0
                    effects = [False for _ in Suit]
                    for card in self.played_cards:
                        total += get_value(card)
                        effects[get_suit(card).value] = True
                    if effects[Suit.JokerSuit.value]:
                        self.joker_used = True
                        self.phase = Phase.JokerChoosePlayer
                        return
                    if effects[Suit.Hearts.value] and (self.joker_used or not get_suit(self.enemy) == Suit.Hearts):
                        self.heal(total)
                    if effects[Suit.Diamonds.value] and (self.joker_used or not get_suit(self.enemy) == Suit.Diamonds):
                        self.draw(total)
                    if effects[Suit.Spades.value]:
                        self.defense += total
                    self.enemy_hp -= total
                    if effects[Suit.Clubs.value] and (self.joker_used or not get_suit(self.enemy) == Suit.Clubs):
                        self.enemy_hp -= total
                    if self.enemy_hp < 1:
                        if self.enemy_hp == 0:
                            self.tavern.append(self.enemy)
                        else:
                            self.discard.append(self.enemy)
                        if self.castle:
                            self.defense = 0
                            for card in self.round_played_cards:
                                self.discard.append(card)
                            for card in self.played_cards:
                                self.discard.append(card)
                            self.round_played_cards = []
                            self.played_cards = []
                            self.enemy = self.castle.pop()
                            self.enemy_hp = get_value(self.enemy)
                        else:
                            self.won = True
                        return
                else:
                    self.yields += 1
                if (self.joker_used or not get_suit(self.enemy) == Suit.Spades) and get_value(self.enemy) - self.defense < 1:
                    self.advance_turn()
                else:
                    self.phase = Phase.Discard
            case Phase.Discard:
                for card in move:
                    self.hands[self.active_player].remove(card)
                    self.discard.append(card)
                self.advance_turn()
            case _:
                self.round_played_cards.extend(self.played_cards)
                self.played_cards = []
                self.active_player = move
                self.phase = Phase.Attack

    def get_legal_actions(self):
        ret = set()
        match self.phase:
            case Phase.Attack:
                if self.yields < len(self.hands):
                    ret.add(frozenset()) # yield
                hand = self.hands[self.active_player]
                hand_length = len(hand)
                for i in range(hand_length):
                    ret.add(frozenset({hand[i]}))
                    value = get_value(hand[i])
                    if value == 1:
                        for j in range(hand_length):
                            if i == j:
                                continue
                            ret.add(frozenset({hand[i], hand[j]}))
                    elif value < 6:
                        matches = set()
                        for j in range(hand_length):
                            if get_value(hand[j]) == value:
                                matches.add(hand[j])
                        for i in range(2, len(matches) + 1):
                            for combo in combinations(matches, i):
                                total = 0
                                for card in combo:
                                    total += get_value(card)
                                if total < 11:
                                    ret.add(frozenset(combo))
            case Phase.Discard: # todo: maybe it should just discard one at a time to reduce action space
                damage = get_value(self.enemy)
                if self.joker_used or not get_suit(self.enemy) == Suit.Spades:
                    damage -= self.defense
                for i in range(1, len(self.hands[self.active_player]) + 1):
                    for combo in combinations(self.hands[self.active_player], i):
                        total = 0
                        for card in combo:
                            total += get_value(card)
                        if total >= damage:
                            ret.add(frozenset(combo))
            case _:
                ret = [p for p in range(len(self.hands))]
        ret = tuple(ret)
        if len(ret) == 0:
            self.lost = True
        return ret

    def is_over(self):
        return self.won or self.lost

    def reward(self):
        if self.won:
            return 1
        if self.lost:
            return -1
        return 0

    def heal(self, amount):
        random.shuffle(self.discard)
        to_heal = []
        while amount > 0 and self.discard:
            to_heal.append(self.discard.pop())
            amount -= 1
        to_heal.extend(self.tavern)
        self.tavern = to_heal

    def draw(self, amount):
        space = self.can_draw()
        next_player = self.active_player
        while amount > 0 and self.tavern and space:
            if len(self.hands[next_player]) < self.max_hand_size:
                self.hands[next_player].append(self.tavern.pop())
                amount -= 1
                space = self.can_draw()
            next_player = (next_player + 1) % len(self.hands)

    def can_draw(self):
        for hand in self.hands:
            if len(hand) < self.max_hand_size:
                return True
        return False


    def advance_turn(self):
        self.round_played_cards.extend(self.played_cards)
        self.played_cards = []
        self.active_player = (self.active_player + 1) % len(self.hands)
        self.phase = Phase.Attack

    def create_castle_deck(self):
        deck = []
        next = [Card.KingOfSpades, Card.KingOfHearts, Card.KingOfDiamonds, Card.KingOfClubs]
        random.shuffle(next)
        deck.extend(next)
        next = [Card.QueenOfSpades, Card.QueenOfHearts, Card.QueenOfDiamonds, Card.QueenOfClubs]
        random.shuffle(next)
        deck.extend(next)
        next = [Card.JackOfSpades, Card.JackOfHearts, Card.JackOfDiamonds, Card.JackOfClubs]
        random.shuffle(next)
        deck.extend(next)
        return deck

    def create_tavern_deck(self):
        deck = []
        i = 0
        while i < 40:
            deck.append(Card(i))
            i += 1
        if len(self.hands) >= 3:
            deck.append(Card.Joker)
        if len(self.hands) == 4:
            deck.append(Card.Joker)
        random.shuffle(deck)
        return deck

    def deal_starting_hands(self):
        for _ in range(self.max_hand_size):
            for hand in self.hands:
                hand.append(self.tavern.pop())