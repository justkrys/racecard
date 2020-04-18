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


"""Finite state machine to track a player's state."""


import dataclasses
import enum

from . import config, deck, exceptions


@enum.unique
class _States(enum.Enum):
    """The states in which a player can be."""

    STOPPED = enum.auto()
    ROLLING = enum.auto()
    BROKEN = enum.auto()
    COMPLETED = enum.auto()


@dataclasses.dataclass
class ScoreCard:
    """A player's score card once the hand is completed."""

    distance: int = 0
    safeties: int = 0
    all_safeties: int = 0
    coups_fourres: int = 0
    trip_completed: int = 0
    delayed_action: int = 0
    safe_trip: int = 0
    shut_out: int = 0
    extension: int = 0
    total: int = 0


@dataclasses.dataclass
class _PlayerState:
    """The state data for a player, including all cards and their positions."""

    state: str
    winner: bool
    hand: tuple
    coups_fourres: int
    sort_hand: bool
    running_total: int
    score_card: ScoreCard
    safeties_pile: tuple = dataclasses.field(default_factory=tuple)
    battle_pile: tuple = dataclasses.field(default_factory=tuple)
    speed_pile: tuple = dataclasses.field(default_factory=tuple)
    distance_pile: tuple = dataclasses.field(default_factory=tuple)


class Player:
    """Represents a player and all their state."""

    def __init__(self):
        self._state = _States.STOPPED
        self._hand = []
        self._safeties_pile = []
        self._battle_pile = []
        self._speed_pile = []
        self._distance_pile = []
        self._coup_fourre_count = 0
        self._last_hazzard_played = None
        self._score_card = None
        self._winner = False
        self._should_sort_hand = False

    # Internal Attributes

    @staticmethod
    def _check_type(card, type_):
        """Raises exception of the card is not of the specificed type."""
        if not card.is_a(type_):
            raise exceptions.InvalidCardError()

    @staticmethod
    def _find_card(pile, type_):
        """Returns the index of the first matching card or None if no card found."""
        for index, card in enumerate(pile):
            if card.is_a(type_):
                return index
        return None

    @property
    def _distance_total(self):
        """Returns the total value of all the distance cards played so far."""
        return sum([card.value for card in self._distance_pile])

    @property
    def _is_limited(self):
        """Returns True if a Speed Limit is in place."""
        if (
            not self._has_right_of_way
            and self._speed_pile
            and self._speed_pile[-1].is_a(deck.SpeedLimitCard)
        ):
            return True
        return False

    @property
    def _has_right_of_way(self):
        """Returns True if deck.RightOfWay is in the safeties pile."""
        return self._has_card(self._safeties_pile, deck.RightOfWayCard)

    def _ensure_not_completed(self):
        """Raises exception if hand is already completed."""
        if self._state == _States.COMPLETED:
            raise exceptions.HandCompletedError()

    def _get_card(self, card_index):
        """Returns the card of the given index.

        Raises and exception if the index is invalid.
        """
        try:
            return self._hand[card_index]
        except IndexError:
            raise exceptions.InvalidCardIndexError()

    def _has_card(self, pile, type_):
        """Returns True if the pile contains a matching card."""
        return self._find_card(pile, type_) is not None

    @staticmethod
    def _move_card(src_pile, dest_pile, card_index):
        """Moves a card from one pile to another."""
        dest_pile.append(src_pile.pop(card_index))

    def _clear_last_hazard(self):
        """Clear the last hazard played to prevent erroneous Coup Fourrés.

        This must be called in on each play successful.
        """
        self._last_hazzard_played = None

    def _sort_hand(self):
        if self._should_sort_hand:
            self._hand.sort(reverse=True, key=lambda card: card.weight)

    # Public Attributes

    @property
    def is_hand_full(self):
        """Returns True if the player's hand is full."""
        return len(self._hand) >= config.MAX_CARDS_IN_HAND

    @property
    def is_hand_empty(self):
        """Returns True if the player's hand is empty."""
        return len(self._hand) == 0

    @property
    def can_coup_fourre(self):
        """Return True if a Coup Fourré is possible."""
        try:
            self.coup_fourre(_test_only=True)
            return True
        except exceptions.CannotCoupFourreError:
            return False

    @property
    def is_winner(self):
        """Returns True if the player believes they have won the hand."""
        return self._winner

    @property
    def is_shutout(self):
        """Returns True if no distance cards have been played."""
        return len(self._distance_pile) == 0

    def card_type(self, card_index):
        """Returns the type of card at the given index.

        e.g. HazardCard, DistanceCard, RemedyCard or SafetyCard.
        """
        self._ensure_not_completed()
        card = self._get_card(card_index)
        types = (deck.SafetyCard, deck.RemedyCard, deck.HazardCard, deck.DistanceCard)
        return [type_ for type_ in types if card.is_a(type_)][0]

    def recieve_card(self, card):
        """Recieve the given card into the player's hand.

        card will be a deck.Card drawn from either the draw or discard pile, or a
        returned hazard card if the hazard play was invalid.

        If self.sort_card is True, then the hand is also sorted by card weight.
        """
        self._ensure_not_completed()
        self._clear_last_hazard()
        self._hand.append(card)

    def play_distance(self, card_index, win_score):
        """Play a distance card and return True if player won.

        card_index is the index number of the card in the player's hand.
        win_score is the score total required to win the hand.
        """
        self._ensure_not_completed()
        card = self._get_card(card_index)
        self._check_type(card, deck.DistanceCard)
        if self._state != _States.ROLLING:
            raise exceptions.InvalidPlayError()
        if self._is_limited and card.value > deck.SpeedLimitCard.max_speed:
            raise exceptions.InvalidPlayError()
        if self._distance_total + card.value > win_score:
            raise exceptions.InvalidPlayError()
        if (
            card.is_a(deck.D200Card)
            and len([c for c in self._distance_pile if c.is_a(deck.D200Card)]) >= 2
        ):
            raise exceptions.InvalidPlayError()
        self._clear_last_hazard()
        self._move_card(self._hand, self._distance_pile, card_index)
        self._sort_hand()
        if self._distance_total == win_score:
            self._state = _States.COMPLETED
            self._winner = True
            return True
        return False

    def extension(self):
        """React to an Extension being called."""
        if self._winner:
            self._state = _States.ROLLING
            self._winner = False

    def play_safety(self, card_index):
        """Play a safety card."""
        self._ensure_not_completed()
        card = self._get_card(card_index)
        self._check_type(card, deck.SafetyCard)
        self._clear_last_hazard()
        self._move_card(self._hand, self._safeties_pile, card_index)
        if self._state == _States.STOPPED and card.is_a(deck.RightOfWayCard):
            self._state = _States.ROLLING
        elif self._state == _States.BROKEN and card.is_a(
            self._battle_pile[-1].prevented_by
        ):
            self._state = _States.STOPPED
            if self._has_right_of_way:
                self._state = _States.ROLLING
        self._sort_hand()

    def play_hazard(self, card_index):
        """Returns the requested hazard card so it can be played on an opponent.

        The card is removed from the hand.
        card_index is the index number of the card in the player's hand.
        """
        self._ensure_not_completed()
        card = self._get_card(card_index)
        self._check_type(card, deck.HazardCard)
        self._clear_last_hazard()
        self._hand.pop(card_index)
        self._sort_hand()
        return card

    def recieve_hazard(self, card):
        """Recieve a hazard card played by an opponent."""
        self._ensure_not_completed()
        self._check_type(card, deck.HazardCard)
        if self._has_card(self._safeties_pile, card.prevented_by):
            raise exceptions.InvalidPlayError()
        if card.is_a(deck.BattleCard):
            if self._state != _States.ROLLING:
                raise exceptions.InvalidPlayError()
            self._battle_pile.append(card)
            if card.is_a(deck.StopCard):
                self._state = _States.STOPPED
            else:
                self._state = _States.BROKEN
        else:  # Must be a Speed Limit then.
            if self._is_limited:
                raise exceptions.InvalidPlayError()
            self._speed_pile.append(card)
        self._last_hazzard_played = card

    def coup_fourre(self, *, _test_only=False):
        """Triggers a Coup Fourré if possible.

        Returns an iterable of cards to discard if Coup Fourré was successful.
        """
        self._ensure_not_completed()
        if self._last_hazzard_played is None:
            raise exceptions.CannotCoupFourreError()
        safety_index = self._find_card(
            self._hand, self._last_hazzard_played.prevented_by,
        )
        if safety_index is None:
            raise exceptions.CannotCoupFourreError()
        if _test_only:
            return []
        safety = self._get_card(safety_index)
        discards = []
        if self._battle_pile:
            top_battle_card = self._battle_pile[-1]
            if top_battle_card.is_a(deck.HazardCard) and safety.is_a(
                top_battle_card.prevented_by
            ):
                self._move_card(self._battle_pile, discards, -1)
                self._state = _States.ROLLING
        if self._speed_pile:
            top_speed_card = self._speed_pile[-1]
            if top_speed_card.is_a(deck.HazardCard) and safety.is_a(
                top_speed_card.prevented_by
            ):
                self._move_card(self._speed_pile, discards, -1)
        self._move_card(self._hand, self._safeties_pile, safety_index)
        self._clear_last_hazard()
        self._coup_fourre_count += 1
        return discards

    def play_remedy(self, card_index):
        """Play a remedy card."""
        self._ensure_not_completed()
        card = self._get_card(card_index)
        self._check_type(card, deck.RemedyCard)
        if self._state == _States.STOPPED and card.is_a(deck.RollCard):
            self._move_card(self._hand, self._battle_pile, card_index)
            self._clear_last_hazard()
            self._state = _States.ROLLING
            self._sort_hand()
            return
        if card.is_a(deck.BattleCard):
            if self._state != _States.BROKEN:
                raise exceptions.InvalidPlayError()
            if not card.is_a(self._battle_pile[-1].remedied_by):
                raise exceptions.InvalidPlayError()
            self._move_card(self._hand, self._battle_pile, card_index)
            self._state = _States.STOPPED
            if self._has_right_of_way:
                self._state = _States.ROLLING
        else:  # SpeedCard
            if not self._is_limited:
                raise exceptions.InvalidPlayError()
            self._move_card(self._hand, self._speed_pile, card_index)
        self._clear_last_hazard()
        self._sort_hand()

    def discard(self, card_index, force=False):
        """Removed card from hand and returns it.

        Attempting to discard a Safety will raise DiscardSafetyWarning unless force is
        set to True.
        """
        self._ensure_not_completed()
        card = self._get_card(card_index)
        if not force and card.is_a(deck.SafetyCard):
            raise exceptions.DiscardSafetyWarning()
        card = self._hand.pop(card_index)
        self._sort_hand()
        return card

    def lost(self):
        """Sets the hand to completed when another player wins."""
        self._winner = False
        self._state = _States.COMPLETED

    def calc_score(self, is_draw_pile_empty, is_extended, is_shutout):
        """Calculates the score card of the player if hand is completed."""
        if self._state != _States.COMPLETED:
            raise exceptions.HandInProgressError()
        if self._score_card is not None:
            return
        # pylint: disable=attribute-defined-outside-init
        card = ScoreCard()
        card.distance = self._distance_total
        safeties_count = len(self._safeties_pile)
        card.safeties = config.SAFETY_SCORE * safeties_count
        if safeties_count == config.TOTAL_SAFETIES:
            card.all_safeties = config.ALL_SAFETIES_SCORE
        card.coups_fourres = config.COUP_FOURRE_SCORE * self._coup_fourre_count
        if self._winner:
            card.trip_completed = config.TRIP_COMPLETED_SCORE
            if is_draw_pile_empty:
                card.delayed_action = config.DELAYED_ACTION_SCORE
            if not any([card.value == 200 for card in self._distance_pile]):
                card.safe_trip = config.SAFE_TRIP_SCORE
            if is_shutout:
                card.shut_out = config.SHUT_OUT_SCORE
            if is_extended:
                card.extension = config.EXTENSION_SCORE
        card.total = sum(dataclasses.astuple(card))
        self._score_card = card

    def get_state(self):
        """Returns a representation of the player's state for display."""
        state = _PlayerState(
            state=self._state.name,
            winner=self._winner,
            coups_fourres=self._coup_fourre_count,
            sort_hand=self._should_sort_hand,
            running_total=self._distance_total,
            hand=tuple(card.name for card in self._hand),
            score_card=self._score_card,
        )
        for name in ("safeties", "battle", "speed", "distance"):
            pile = getattr(self, f"_{name}_pile")
            setattr(state, f"{name}_pile", tuple(card.name for card in pile))
        return state

    def toggle_sort(self):
        """Toggles whether or not the player's hand should always be sorted."""
        self._ensure_not_completed()
        self._should_sort_hand = not self._should_sort_hand
        self._sort_hand()
