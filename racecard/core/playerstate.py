
from racecard.core import deck


class PlayerState:

    def __init__(self):
        self.hand = []
        self.safeties = []  # All safeties, including the coup fourré cards.
        self.coups_fourres = []  # The safeties that were also coups fourrés.
        self.battle_pile = []
        self.speed_pile = []
        self.distance_pile = []

    @property
    def has_drawn(self):
        return len(self.hand) == 7

    @property
    def all_safeties(self):
        return self.safeties + self.coups_fourres

    @property
    def total(self):
        return sum(card.value for card in self.distance_pile)

    @property
    def is_rolling(self):
        if self.battle_pile and self.battle_pile[-1].type is deck.RemedyTypes.ROLL:
            return True
        if any([card.type is deck.SafetyTypes.RIGHT_OF_WAY for card in self.all_safeties]):
            return True
        return False
