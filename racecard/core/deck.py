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
from abc import ABC, abstractmethod

from racecard.core import config

# Base Classes


class Card(ABC):  # pylint: disable=too-few-public-methods

    """Base class for all cards."""

    @property
    @abstractmethod
    def name(self):
        """The name of the card."""

    @property
    @abstractmethod
    def weight(self):
        """A weight number of the card when sorting a hand. Higher = more top/left."""

    def __str__(self):
        return self.name

    def is_a(self, type_):
        """Returns True if the card is an instance of the given type."""
        return isinstance(self, type_)


class SafetyCard(Card):  # pylint: disable=too-few-public-methods,abstract-method
    """Safety cards both recover, prevent and even interrupt the playing of hazards."""


class BattleCard(Card):  # pylint: disable=too-few-public-methods,abstract-method
    """Cards that go on the battle pile."""


class SpeedCard(Card):  # pylint: disable=too-few-public-methods,abstract-method
    """Cards that go on the speed pile."""


class RemedyCard(Card):  # pylint: disable=too-few-public-methods,abstract-method
    """Remedy cards recover from hazards."""


class HazardCard(Card):  # pylint: disable=too-few-public-methods
    """Hazard cards are for attacking opponents."""

    @property
    @abstractmethod
    def remedied_by(self):
        """Can be remedied by this card type."""

    @property
    @abstractmethod
    def prevented_by(self):
        """Can be prevented by this card type."""


class DistanceCard(Card):  # pylint: disable=too-few-public-methods
    """Distance cards increase player scores."""

    @property
    @abstractmethod
    def value(self):
        """The numeric value of the card."""

    @property
    def name(self):
        return str(self.value)


# Safety Cards


class DrivingAceCard(SafetyCard):  # pylint: disable=too-few-public-methods
    """Driving Ace recovers and prevents Accident.  It is also an interrupt."""

    name = "Driving Ace"
    weight = config.DRIVING_ACE_WEIGHT


class ExtraTankCard(SafetyCard):  # pylint: disable=too-few-public-methods
    """Extra Tank recovers and prevents Out of Gass.  It is also an interrupt."""

    name = "Extra Tank"
    weight = config.EXTRA_TANK_WEIGHT


class PunctureProofCard(SafetyCard):  # pylint: disable=too-few-public-methods
    """Puncture Proof recovers and prevents Flat Tire.  It is also an interrupt."""

    name = "Puncture Proof"
    weight = config.PUNCTURE_PROOF_WEIGHT


class RightOfWayCard(SafetyCard):  # pylint: disable=too-few-public-methods
    """Right of Way recovers and prevents Stop and Speed Limit. It is also an interrupt.

    It also negates the need to play Roll cards completely.
    """

    name = "Right of Way"
    weight = config.RIGHT_OF_WAY_WEIGHT


# Remedy Cards


class EndOfLimitCard(SpeedCard, RemedyCard):  # pylint: disable=too-few-public-methods
    """End of Limit recovers from Speed Limit and is superceeded by Right of Way."""

    name = "End of Limit"
    weight = config.END_OF_LIMIT_WEIGHT


class SpareTireCard(BattleCard, RemedyCard):  # pylint: disable=too-few-public-methods
    """Spare Tire recovers from Flat Tire and is superceeded by Puncture Proof."""

    name = "Spare Tire"
    weight = config.SPARE_TIRE_WEIGHT


class RepairsCard(BattleCard, RemedyCard):  # pylint: disable=too-few-public-methods
    """Repairs recovers from Accident and is superceeded by Driving Ace."""

    name = "Repairs"
    weight = config.REPAIRS_WEIGHT


class GasolineCard(BattleCard, RemedyCard):  # pylint: disable=too-few-public-methods
    """Gasoline recovers from Out of Gas and is superceeded by Extra Tank."""

    name = "Gasoline"
    weight = config.GASOLINE_WEIGHT


class RollCard(BattleCard, RemedyCard):  # pylint: disable=too-few-public-methods
    """Roll recovers from Stop and is superceeded by Right of Way.

    It is also needed after all remedied hazards except Speed Limit/End of Limit.
    """

    name = "Roll"
    weight = config.ROLL_WEIGHT


# Hazard Cards


class SpeedLimitCard(SpeedCard, HazardCard):  # pylint: disable=too-few-public-methods
    """Speed Limit slows an opponent by restricting distance cards use.

    They need End of Limit to recover.
    """

    name = "Speed Limit"
    weight = config.SPEED_LIMIT_WEIGHT
    remedied_by = EndOfLimitCard
    prevented_by = RightOfWayCard
    max_speed = config.SPEED_LIMIT_LIMIT


class StopCard(BattleCard, HazardCard):  # pylint: disable=too-few-public-methods
    """Stop stops an opponent. They need Roll to recover."""

    name = "Stop"
    weight = config.STOP_WEIGHT
    remedied_by = RollCard
    prevented_by = RightOfWayCard


class OutOfGasCard(BattleCard, HazardCard):  # pylint: disable=too-few-public-methods
    """Out of Gas stops an opponent. They need Gasoline and Roll to recover."""

    name = "Out of Gas"
    weight = config.OUT_OF_GASS_WEIGHT
    remedied_by = GasolineCard
    prevented_by = ExtraTankCard


class FlatTireCard(BattleCard, HazardCard):  # pylint: disable=too-few-public-methods
    """Flat Tire stops an opponent. They need Spare Tire and Roll to recover."""

    name = "Flat Tire"
    weight = config.FLAT_TIRE_WEIGHT
    remedied_by = SpareTireCard
    prevented_by = PunctureProofCard


class AccidentCard(BattleCard, HazardCard):  # pylint: disable=too-few-public-methods
    """Accident stops an opponent. They need Repairs and Roll to recover."""

    name = "Accident"
    weight = config.ACCIDENT_WEIGHT
    remedied_by = RepairsCard
    prevented_by = DrivingAceCard


# Distance Cards


class D25Card(DistanceCard):  # pylint: disable=too-few-public-methods
    """Travel 25 km."""

    value = 25
    weight = config.D25_WEIGHT


class D50Card(DistanceCard):  # pylint: disable=too-few-public-methods
    """Travel 50 km."""

    value = 50
    weight = config.D50_WEIGHT


class D75Card(DistanceCard):  # pylint: disable=too-few-public-methods
    """Travel 75 km."""

    value = 75
    weight = config.D75_WEIGHT


class D100Card(DistanceCard):  # pylint: disable=too-few-public-methods
    """Travel 100 km."""

    value = 100
    weight = config.D100_WEIGHT


class D200Card(DistanceCard):  # pylint: disable=too-few-public-methods
    """Travel 200 km.

    Also lose the Safe Trip score bonus.
    """

    value = 200
    weight = config.D200_WEIGHT


# Constants 2

# NOTE: We are using multiple references to single instances for our deck's contents.
#       I.e. All AccidentCards are the same instance.  When removing a card from the
#       deck, or moving a card to another list, it is the specific reference we want to
#       (re)move, not the whole instance.
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


def make_deck(small=False):
    """Make a new deck, shuffle it and return it."""
    new_deck = _BASE_DECK.copy()
    _add_hazards(new_deck, small)
    for _ in range(config.NUM_SHUFFLES):
        random.shuffle(new_deck)
    return new_deck
