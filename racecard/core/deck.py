
import random
from enum import Enum, unique, auto
from collections import abc


# Constants

DEFAULT_NUM_SHUFFLES = 3


@unique
class CardKinds(Enum):
    HAZARD = auto()
    REMEDY = auto()
    SAFETY = auto()
    DISTANCE = auto()


@unique
class CardPiles(Enum):
    BATTLE = auto()
    SPEED = auto()
    SAFETY = auto()
    DISTANCE = auto()


@unique
class HazardTypes(Enum):
    ACCIDENT = auto()
    OUT_OF_GAS = auto()
    FLAT_TIRE = auto()
    STOP = auto()
    SPEED_LIMIT = auto()


@unique
class RemedyTypes(Enum):
    REPAIRS = auto()
    GASOLINE = auto()
    SPARE_TIRE = auto()
    ROLL = auto()
    END_OF_LIMIT = auto()


@unique
class SafetyTypes(Enum):
    DRIVING_ACE = auto()
    EXTRA_TANK = auto()
    PUNCTURE_PROOF = auto()
    RIGHT_OF_WAY = auto()


@unique
class DistanceTypes(Enum):
    D25 = 25
    D50 = 50
    D75 = 75
    D100 = 100
    D200 = 200


# Base Classes

class Card:

    def __init__(self, kind, type_, pile):
        self.kind = kind
        self.type = type_
        self.pile = pile

    def __repr__(self):
        return f'Card({self.kind.name}, {self.type.name}, {self.pile.name})'

    def __str__(self):
        return self.type.name.replace('_', ' ').title()

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.kind == other.kind and self.type == other.type and self.pile == other.pile


class HazardCard(Card):

    def __init__(self, type_, remedied_by, prevented_by, pile=CardPiles.BATTLE):
        super().__init__(CardKinds.HAZARD, type_, pile)
        self.remedied_by = remedied_by
        self.prevented_by = prevented_by


class RemedyCard(Card):

    def __init__(self, type_, applies_to, superseded_by, pile=CardPiles.BATTLE):
        super().__init__(CardKinds.REMEDY, type_, pile)
        self.applies_to = ({applies_to} if not isinstance(applies_to, abc.Iterable) else set(applies_to))
        self.superseded_by = superseded_by


class SafetyCard(Card):

    def __init__(self, type_, prevents, supersedes):
        super().__init__(CardKinds.SAFETY, type_, CardPiles.SAFETY)
        self.prevents = ({prevents} if not isinstance(prevents, abc.Iterable) else set(prevents))
        self.supersedes = supersedes


class DistanceCard(Card):

    def __init__(self, type_, prevented_by=None):
        super().__init__(CardKinds.DISTANCE, type_, CardPiles.DISTANCE)
        self.prevented_by = prevented_by

    def __str__(self):
        return super().__str__()[1:]  # Strip initial D character

    @property
    def value(self):
        return self.type.value


# Hazard Cards

class AccidentCard(HazardCard):

    def __init__(self):
        super().__init__(HazardTypes.ACCIDENT, RemedyTypes.REPAIRS, SafetyTypes.DRIVING_ACE)


class OutOfGasCard(HazardCard):

    def __init__(self):
        super().__init__(HazardTypes.OUT_OF_GAS, RemedyTypes.GASOLINE, SafetyTypes.EXTRA_TANK)


class FlatTireCard(HazardCard):

    def __init__(self):
        super().__init__(HazardTypes.FLAT_TIRE, RemedyTypes.SPARE_TIRE, SafetyTypes.PUNCTURE_PROOF)


class StopCard(HazardCard):

    def __init__(self):
        super().__init__(HazardTypes.STOP, RemedyTypes.ROLL, SafetyTypes.RIGHT_OF_WAY)


class SpeedLimitCard(HazardCard):

    def __init__(self):
        super().__init__(HazardTypes.SPEED_LIMIT, RemedyTypes.END_OF_LIMIT, SafetyTypes.RIGHT_OF_WAY, CardPiles.SPEED)


# Remedy Cards

class RepairsCard(RemedyCard):

    def __init__(self):
        super().__init__(RemedyTypes.REPAIRS, HazardTypes.ACCIDENT, SafetyTypes.DRIVING_ACE)


class GasolineCard(RemedyCard):

    def __init__(self):
        super().__init__(RemedyTypes.GASOLINE, HazardTypes.OUT_OF_GAS, SafetyTypes.EXTRA_TANK)


class SpareTireCard(RemedyCard):

    def __init__(self):
        super().__init__(RemedyTypes.SPARE_TIRE, HazardTypes.FLAT_TIRE, SafetyTypes.PUNCTURE_PROOF)


class RollCard(RemedyCard):

    def __init__(self):
        applies_to = set(RemedyTypes)
        applies_to.remove(RemedyTypes.ROLL)
        applies_to.add(HazardTypes.STOP)
        super().__init__(RemedyTypes.ROLL, applies_to, SafetyTypes.RIGHT_OF_WAY)


class EndOfLimitCard(RemedyCard):

    def __init__(self):
        super().__init__(RemedyTypes.END_OF_LIMIT, HazardTypes.SPEED_LIMIT, SafetyTypes.RIGHT_OF_WAY, CardPiles.SPEED)


# Safety Cards

class DrivingAceCard(SafetyCard):

    def __init__(self):
        super().__init__(SafetyTypes.DRIVING_ACE, HazardTypes.ACCIDENT, RemedyTypes.REPAIRS)


class ExtraTankCard(SafetyCard):

    def __init__(self):
        super().__init__(SafetyTypes.EXTRA_TANK, HazardTypes.OUT_OF_GAS, RemedyTypes.GASOLINE)


class PunctureProofCard(SafetyCard):

    def __init__(self):
        super().__init__(SafetyTypes.PUNCTURE_PROOF, HazardTypes.FLAT_TIRE, RemedyTypes.SPARE_TIRE)


class RightOfWayCard(SafetyCard):

    def __init__(self):
        super().__init__(SafetyTypes.RIGHT_OF_WAY, (HazardTypes.STOP, HazardTypes.SPEED_LIMIT), RemedyTypes.ROLL)


# Distance Cards

class D25Card(DistanceCard):

    def __init__(self):
        super().__init__(DistanceTypes.D25)


class D50Card(DistanceCard):

    def __init__(self):
        super().__init__(DistanceTypes.D50)


class D75Card(DistanceCard):

    def __init__(self):
        super().__init__(DistanceTypes.D75, HazardTypes.SPEED_LIMIT)


class D100Card(DistanceCard):

    def __init__(self):
        super().__init__(DistanceTypes.D100, HazardTypes.SPEED_LIMIT)


class D200Card(DistanceCard):

    def __init__(self):
        super().__init__(DistanceTypes.D200, HazardTypes.SPEED_LIMIT)


# Constants 2

TOTAL_SAFETIES = 4

# NOTE: We are using multiple references to single instances for our deck's contents.  I.e. All AccidentCards are the
#       same instance.  When removing a card from the deck, or moving a card to another list, it is the specific
#       reference we want to (re)move, not the whole instance.
_BASE_DECK = [
    *([RepairsCard()] * 6),
    *([GasolineCard()] * 6),
    *([SpareTireCard()] * 6),
    *([RollCard()] * 14),
    *([EndOfLimitCard()] * 6),

    DrivingAceCard(),
    ExtraTankCard(),
    PunctureProofCard(),
    RightOfWayCard(),

    *([D25Card()] * 10),
    *([D50Card()] * 10),
    *([D75Card()] * 10),
    *([D100Card()] * 12),
    *([D200Card()] * 4),
]


# Functions

def _add_hazards(deck, small):
    extra = (0 if small else 1)
    deck.extend([
        *([AccidentCard()] * (2 + extra)),
        *([OutOfGasCard()] * (2 + extra)),
        *([FlatTireCard()] * (2 + extra)),
        *([StopCard()] * (4 + extra)),
        *([SpeedLimitCard()] * (3 + extra)),
    ])


def make_deck(small=False, num_shuffles=DEFAULT_NUM_SHUFFLES):
    new_deck = _BASE_DECK.copy()
    _add_hazards(new_deck, small)
    for _ in range(num_shuffles):
        random.shuffle(new_deck)
    return new_deck
