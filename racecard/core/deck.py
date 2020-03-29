#    Race Card - An implementation of the card game Mille Bornes
#    Copyright (C) 2020  Krys Lawrence <krys AT krys DOT ca>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Define all card types and create decks from which to draw."""


import random
from collections import abc
from enum import Enum, auto, unique

# Constants

DEFAULT_NUM_SHUFFLES = 3


@unique
class CardKinds(Enum):
    """Each card has a kind (or class or category), they are enumerated here."""

    HAZARD = auto()
    REMEDY = auto()
    SAFETY = auto()
    DISTANCE = auto()


@unique
class CardPileTypes(Enum):
    """Each card can only go in certain piles, the pile types are enumerated here."""

    BATTLE = auto()
    SPEED = auto()
    SAFETY = auto()
    DISTANCE = auto()


@unique
class HazardTypes(Enum):
    """Hazard cards are for attacking opponents, the types are enumarated here."""

    ACCIDENT = auto()
    OUT_OF_GAS = auto()
    FLAT_TIRE = auto()
    STOP = auto()
    SPEED_LIMIT = auto()


@unique
class RemedyTypes(Enum):
    """Remedy cards recover from hazards, the types are enumarated here."""

    REPAIRS = auto()
    GASOLINE = auto()
    SPARE_TIRE = auto()
    ROLL = auto()
    END_OF_LIMIT = auto()


@unique
class SafetyTypes(Enum):
    """Safety cards both recover and prevent hazards, the types are enumarated here.

    They can also be used to interrupt the playing of a hazard.
    """

    DRIVING_ACE = auto()
    EXTRA_TANK = auto()
    PUNCTURE_PROOF = auto()
    RIGHT_OF_WAY = auto()


@unique
class DistanceTypes(Enum):
    """Distance cards increase player scores, the types are enumarated here."""

    D25 = 25
    D50 = 50
    D75 = 75
    D100 = 100
    D200 = 200


# Base Classes


class Card:
    """Base class for all cards."""

    def __init__(self, kind, type_, pile_type):
        self.kind = kind
        self.type = type_
        self.pile_type = pile_type

    def __repr__(self):
        return f"Card({self.kind.name}, {self.type.name}, {self.pile_type.name})"

    def __str__(self):
        return self.type.name.replace("_", " ").title()

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return (
            self.kind == other.kind
            and self.type == other.type
            and self.pile_type == other.pile_type
        )


class HazardCard(Card):
    """Hazard cards are for attacking opponents."""

    def __init__(
        self, type_, remedied_by, prevented_by, pile_type=CardPileTypes.BATTLE
    ):
        super().__init__(CardKinds.HAZARD, type_, pile_type)
        self.remedied_by = remedied_by
        self.prevented_by = prevented_by


class RemedyCard(Card):
    """Remedy cards recover from hazards/"""

    def __init__(
        self, type_, applies_to, superseded_by, pile_type=CardPileTypes.BATTLE
    ):
        super().__init__(CardKinds.REMEDY, type_, pile_type)
        self.applies_to = (
            {applies_to}
            if not isinstance(applies_to, abc.Iterable)
            else set(applies_to)
        )
        self.superseded_by = superseded_by


class SafetyCard(Card):
    """Safety cards both recover, prevent and even interrupt the playing of hazards."""

    def __init__(self, type_, prevents, supersedes):
        super().__init__(CardKinds.SAFETY, type_, CardPileTypes.SAFETY)
        self.prevents = (
            {prevents} if not isinstance(prevents, abc.Iterable) else set(prevents)
        )
        self.supersedes = supersedes


class DistanceCard(Card):
    """Distance cards increase player scores."""

    def __init__(self, type_, prevented_by=None):
        super().__init__(CardKinds.DISTANCE, type_, CardPileTypes.DISTANCE)
        self.prevented_by = prevented_by

    def __str__(self):
        return super().__str__()[1:]  # Strip initial D character

    @property
    def value(self):
        """Returns the distance value of the card."""
        return self.type.value


# Hazard Cards


class AccidentCard(HazardCard):
    """Accident stops an opponent. They need Repairs and ROll to recover."""

    def __init__(self):
        super().__init__(
            HazardTypes.ACCIDENT, RemedyTypes.REPAIRS, SafetyTypes.DRIVING_ACE
        )


class OutOfGasCard(HazardCard):
    """Out of Gas stops an opponent. They need Gasoline and Roll to recover."""

    def __init__(self):
        super().__init__(
            HazardTypes.OUT_OF_GAS, RemedyTypes.GASOLINE, SafetyTypes.EXTRA_TANK
        )


class FlatTireCard(HazardCard):
    """Flat Tire stops an opponent. They need Spare Tire and Roll to recover."""

    def __init__(self):
        super().__init__(
            HazardTypes.FLAT_TIRE, RemedyTypes.SPARE_TIRE, SafetyTypes.PUNCTURE_PROOF
        )


class StopCard(HazardCard):
    """Stop stops an opponent. They need Roll to recover."""

    def __init__(self):
        super().__init__(HazardTypes.STOP, RemedyTypes.ROLL, SafetyTypes.RIGHT_OF_WAY)


class SpeedLimitCard(HazardCard):
    """Speed Limit slows an opponent by restricting distance cards use.

    They need End of Limit to recover.
    """

    def __init__(self):
        super().__init__(
            HazardTypes.SPEED_LIMIT,
            RemedyTypes.END_OF_LIMIT,
            SafetyTypes.RIGHT_OF_WAY,
            CardPileTypes.SPEED,
        )


# Remedy Cards


class RepairsCard(RemedyCard):
    """Repairs recovers from Accident and is superceeded by Driving Ace."""

    def __init__(self):
        super().__init__(
            RemedyTypes.REPAIRS, HazardTypes.ACCIDENT, SafetyTypes.DRIVING_ACE
        )


class GasolineCard(RemedyCard):
    """Gasoline recovers from Out of Gas and is superceeded by Extra Tank."""

    def __init__(self):
        super().__init__(
            RemedyTypes.GASOLINE, HazardTypes.OUT_OF_GAS, SafetyTypes.EXTRA_TANK
        )


class SpareTireCard(RemedyCard):
    """Spare Tire recovers from Flat Tire and is superceeded by Puncture Proof."""

    def __init__(self):
        super().__init__(
            RemedyTypes.SPARE_TIRE, HazardTypes.FLAT_TIRE, SafetyTypes.PUNCTURE_PROOF
        )


class RollCard(RemedyCard):
    """Roll recovers from Stop and is superceeded by Right of Way.

    It is also needed after all remedied hazards except Speed Limit/End of Limit.
    """

    def __init__(self):
        applies_to = set(RemedyTypes)
        applies_to.remove(RemedyTypes.ROLL)
        applies_to.add(HazardTypes.STOP)
        super().__init__(RemedyTypes.ROLL, applies_to, SafetyTypes.RIGHT_OF_WAY)


class EndOfLimitCard(RemedyCard):
    """End of Limit recovers from Speed Limit and is superceeded by Right of Way."""

    def __init__(self):
        super().__init__(
            RemedyTypes.END_OF_LIMIT,
            HazardTypes.SPEED_LIMIT,
            SafetyTypes.RIGHT_OF_WAY,
            CardPileTypes.SPEED,
        )


# Safety Cards


class DrivingAceCard(SafetyCard):
    """Driving Ace recovers and prevents Accident.  It is also an interrupt."""

    def __init__(self):
        super().__init__(
            SafetyTypes.DRIVING_ACE, HazardTypes.ACCIDENT, RemedyTypes.REPAIRS
        )


class ExtraTankCard(SafetyCard):
    """Extra Tank recovers and prevents Out of Gass.  It is also an interrupt."""

    def __init__(self):
        super().__init__(
            SafetyTypes.EXTRA_TANK, HazardTypes.OUT_OF_GAS, RemedyTypes.GASOLINE
        )


class PunctureProofCard(SafetyCard):
    """Puncture Proof recovers and prevents Flat Tire.  It is also an interrupt."""

    def __init__(self):
        super().__init__(
            SafetyTypes.PUNCTURE_PROOF, HazardTypes.FLAT_TIRE, RemedyTypes.SPARE_TIRE
        )


class RightOfWayCard(SafetyCard):
    """Right of Way recovers and prevents Stop and Speed Limit. It is also an interrupt.

    It also negates the need to play Roll cards completely.
    """

    def __init__(self):
        super().__init__(
            SafetyTypes.RIGHT_OF_WAY,
            (HazardTypes.STOP, HazardTypes.SPEED_LIMIT),
            RemedyTypes.ROLL,
        )


# Distance Cards


class D25Card(DistanceCard):
    """Travel 25 km."""

    def __init__(self):
        super().__init__(DistanceTypes.D25)


class D50Card(DistanceCard):
    """Travel 50 km."""

    def __init__(self):
        super().__init__(DistanceTypes.D50)


class D75Card(DistanceCard):
    """Travel 75 km."""

    def __init__(self):
        super().__init__(DistanceTypes.D75, HazardTypes.SPEED_LIMIT)


class D100Card(DistanceCard):
    """Travel 100 km."""

    def __init__(self):
        super().__init__(DistanceTypes.D100, HazardTypes.SPEED_LIMIT)


class D200Card(DistanceCard):
    """Travel 200 km.

    Also lose the Safe Trip score bonus.
    """

    def __init__(self):
        super().__init__(DistanceTypes.D200, HazardTypes.SPEED_LIMIT)


# Constants 2

TOTAL_SAFETIES = 4

# NOTE: We are using multiple references to single instances for our deck's contents.
#       I.e. All AccidentCards are the same instance.  When removing a card from the
#       deck, or moving a card to another list, it is the specific reference we want to
#       (re)move, not the whole instance.
# TODO: Would weakrefs be better here?
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
    """Adds hazards to a deck.  Large decks get extra hazards."""
    extra = 0 if small else 1
    deck.extend(
        [
            *([AccidentCard()] * (2 + extra)),
            *([OutOfGasCard()] * (2 + extra)),
            *([FlatTireCard()] * (2 + extra)),
            *([StopCard()] * (4 + extra)),
            *([SpeedLimitCard()] * (3 + extra)),
        ]
    )


def make_deck(small=False, num_shuffles=DEFAULT_NUM_SHUFFLES):
    """Make a new deck, shuffle it and return it."""
    new_deck = _BASE_DECK.copy()
    _add_hazards(new_deck, small)
    for _ in range(num_shuffles):
        random.shuffle(new_deck)
    return new_deck
