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


"""Top-level of core.  The Game class runs a whole game."""


import dataclasses
import enum
import random
import typing
import uuid

from . import config, exceptions, hand, player


@enum.unique
class GameStates(enum.Enum):
    """The states in which a game can be."""

    NOTBEGUN = enum.auto()
    RUNNING = enum.auto()
    COMPLETED = enum.auto()


@dataclasses.dataclass
class _PlayerData:
    """Stores game-level player data."""

    sort_hand: bool = False  # Remembers toggle_sort() choice between hands.
    score_card: typing.Optional[player.ScoreCard] = None


@dataclasses.dataclass
class _GameScoreCard(player.ScoreCard):

    game_total: int = 0

    @classmethod
    def from_score_card(cls, score_card, game_total=0):
        """Returns a new instance based on the given score card."""
        attributes = {
            name: getattr(score_card, name) for name in score_card.__dataclass_fields__
        }
        return cls(game_total=game_total, **attributes)


class Game:
    """Top-level Game class.  Registers players and runs multiple hands.

    Servers/applications should instantiate this class.
    """

    def __init__(self):
        self._players = {}  # Stores player ids and game-level player data.
        self._turn_order = []
        self._hands = []
        self.winner_id = None
        self.state = GameStates.NOTBEGUN

    # Internal Attributes

    @property
    def _current_hand(self):
        """Returns the current hand object."""
        self._ensure_begun()
        return self._hands[-1]

    def _ensure_begun(self):
        """Raises exception of the game is not yet begun."""
        if self.state == GameStates.NOTBEGUN:
            raise exceptions.NotBegunError()

    def _ensure_not_begun(self):
        """Raises exception of the game has already begun."""
        if self.state != GameStates.NOTBEGUN:
            raise exceptions.GameAlreadyBegun()

    def _ensure_not_completed(self):
        """Raises exception of the game has already completed."""
        if self.state == GameStates.COMPLETED:
            raise exceptions.GameAlreadyCompleted()

    def _get_game_total(self, player_id):
        """Calculates and returns the current game total for the given player."""
        self._ensure_begun()
        game_total = 0
        for hand_ in self._hands:
            score_card = hand_.get_player_state(player_id).score_card
            if score_card:
                game_total += score_card.total
        return game_total

    def _check_game_complete(self):
        """Checks if the game is completed and updates status accordingly."""
        self._ensure_begun()
        if self.is_completed or not self.is_hand_completed:
            return
        game_totals = {
            player_id: self._get_game_total(player_id) for player_id in self._players
        }
        if any(
            True for total in game_totals.values() if total >= config.GAME_WIN_SCORE
        ):
            self.state = GameStates.COMPLETED
            self.winner_id = max(
                game_totals, key=lambda player_id: game_totals[player_id]
            )

    @staticmethod
    def _make_player_id():
        """Create a new unique player ID.

        Player IDs must be hashable so they can be used as dictionary keys and in sets.

        Default implementation is a UUID v4.
        """
        return uuid.uuid4()

    # Public Attributes

    @property
    def hand_number(self):
        """Returns the number of the current hand."""
        self._ensure_begun()
        return len(self._hands)

    @property
    def is_completed(self):
        """Returns True if the game is completed/finished/done."""
        return self.state == GameStates.COMPLETED

    def add_player(self):
        """Adds a new player to the game and retruns their id."""
        self._ensure_not_begun()
        if len(self._players) > config.MAX_PLAYERS:
            raise exceptions.TooManyPlayers()
        new_id = self._make_player_id()
        self._players[new_id] = _PlayerData()
        return new_id

    def begin(self):
        """Begin the game or raise InsufficientPlayersError if not enough players."""
        self._ensure_not_begun()
        if len(self._players) < 2:
            raise exceptions.InsufficientPlayersError()
        self._turn_order = list(self._players)
        for _ in range(config.NUM_SHUFFLES):
            random.shuffle(self._turn_order)
        self.state = GameStates.RUNNING
        self.next_hand()

    def next_hand(self):
        """Creates a new hand or HandInProgressError if current one is still going."""
        self._ensure_begun()
        self._ensure_not_completed()
        if self._hands and not self._current_hand.is_completed:
            raise exceptions.HandInProgressError()
        self._turn_order.append(self._turn_order.pop(0))
        next_hand = hand.Hand(self._turn_order)
        # Preserve toggle_sort() setting between hands.
        for id_, data in self._players.items():
            if data.sort_hand:
                next_hand.toggle_sort(id_)
        self._hands.append(next_hand)

    def get_hand_scores(self):
        """Returns the current hand score cards for all players.

        Only  called once the current hand is completed.
        Also includes a game_total attribute.
        """
        self._ensure_begun()
        if not self.is_hand_completed:
            raise exceptions.HandInProgressError()
        score_cards = {}
        for player_id in self._players:
            # score_card always exists because hand is guraranteed completed by check
            # above.
            score_card = self.get_player_state(player_id).score_card
            # game_total includes current hand because it is guraranteed completed by
            # check above.
            game_total = self._get_game_total(player_id)
            score_card = _GameScoreCard.from_score_card(score_card, game_total)
            score_cards[player_id] = score_card
        return score_cards

    def get_game_scores(self):
        """Returns game-total score cards for all players once the game is completed."""
        if not self.is_completed:
            raise exceptions.GameNotCompleted()
        for id_, data in self._players.items():
            if data.score_card is not None:
                continue  # Already calculated
            game_card = data.score_card = player.ScoreCard()
            for hand_ in self._hands:
                hand_card = hand_.get_player_state(id_).score_card
                for point_type, hand_score in dataclasses.asdict(hand_card).items():
                    current_score = getattr(game_card, point_type)
                    setattr(game_card, point_type, current_score + hand_score)
        return {id_: data.score_card for id_, data in self._players.items()}

    # Overridden Hand attributes

    @property
    def is_hand_completed(self):
        """Returns True if the current hand is completed."""
        # Overridden to change name
        self._ensure_begun()
        return self._current_hand.is_completed

    @property
    def hand_winner_id(self):
        """Returns the id of the player who won the current hand, if possible."""
        # Overridden to change name
        self._ensure_begun()
        return self._current_hand.winner_id

    def play(self, player_id, card_index, targed_id=None):
        """Passes a play to the current hand and returns the result.

        Also updates game state when necessary (i.e. winning the whole game).

        target_id is only used for hazards.
        If target_id is None, and this is a 2-player game, then the other player is
        automatically selected as the target.
        """
        # This overrides Hand.play to include extra game-level logic.
        self._ensure_begun()
        self._ensure_not_completed()
        result = self._current_hand.play(player_id, card_index, targed_id)
        if result == hand.PlayResults.WIN_CANNOT_EXTEND:
            self._check_game_complete()
        return result

    def toggle_sort(self, player_id):
        """Toggles whether or not a player's hand should always be sorted."""
        # This overrides Hand.play to include extra game-level logic.
        self._ensure_begun()
        self._ensure_not_completed()
        self._current_hand.toggle_sort(player_id)
        self._players[player_id].sort_hand = not self._players[player_id].sort_hand

    def discard(self, player_id, card_index, force=False):
        """Discards a card from the player's hand.

        Attempting to discard a Safety will raise DiscardSafetyWarning unless force is
        set to True.
        """
        # This overrides Hand.play to include extra game-level logic.
        self._ensure_begun()
        self._ensure_not_completed()
        self._current_hand.discard(player_id, card_index, force)
        self._check_game_complete()

    def no_extension(self, player_id):
        """Signal that an extension was declined and the hand should complete."""
        # This overrides Hand.play to include extra game-level logic.
        self._ensure_begun()
        self._ensure_not_completed()
        self._current_hand.no_extension(player_id)
        self._check_game_complete()

    # Non-overridden Hand attributes

    @property
    def round_number(self):
        """Returns the number of the current round."""
        self._ensure_begun()
        return self._current_hand.round_number

    @property
    def current_player_id(self):
        """Returns the id of the current player."""
        self._ensure_begun()
        return self._current_hand.current_player_id

    @property
    def cards_remaining(self):
        """Returns the number of cards left in the deck."""
        self._ensure_begun()
        return self._current_hand.cards_remaining

    @property
    def top_discarded_card(self):
        """Returns the top card on the discarded pile.

        Note: It does not remove the card from the pile. It just peeks at it.
        """
        self._ensure_begun()
        return self._current_hand.top_discarded_card

    def draw(self, player_id, discard=False):
        """Draw a card from either the draw or discard pile."""
        self._ensure_begun()
        self._ensure_not_completed()
        self._current_hand.draw(player_id, discard)

    def coup_fourre(self, player_id):
        """Triggers a Coup Fourré if possible."""
        self._ensure_begun()
        self._ensure_not_completed()
        self._current_hand.coup_fourre(player_id)

    def extension(self, player_id):
        """Call an extension to the game."""
        self._ensure_begun()
        self._ensure_not_completed()
        self._current_hand.extension(player_id)

    def get_player_state(self, player_id):
        """Returns the state of the given player."""
        self._ensure_begun()
        return self._current_hand.get_player_state(player_id)
