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


"""Race Card server implementation for running locally without a network."""


from contextlib import contextmanager

from racecard.core import exceptions, game
from racecard.server import base


class LocalServerError(base.ServerError):
    """Exception class for all LocalServer errors."""


@contextmanager
def _game_exceptions():
    """Conext manager for handling core errors.

    Core exceptions are encapsulated as LocalServerError exceptions.
    """
    try:
        yield
    except exceptions.CoreException as error:
        raise LocalServerError(str(error)) from error


class LocalServer(base.ServerBase):
    """A Race Card server for local (non-network) gameplay."""

    def __init__(self):
        self._game = game.Game()

    # Game Methods

    def add_player(self):
        """Add a player to the game and return their id."""
        return self._game.join()

    def start_game(self):
        """Start the game."""
        with _game_exceptions():
            self._game.begin()

    # Hand Methods

    @property
    def hand_number(self):
        """Return the number of the current hand."""
        with _game_exceptions():
            return self._game.current_hand.number

    @property
    def round_number(self):
        """Return the number of the current round."""
        with _game_exceptions():
            return self._game.current_hand.round

    @property
    def is_hand_completed(self):
        """Return True is the current hand has completed."""
        with _game_exceptions():
            return self._game.current_hand.is_completed

    @property
    def is_hand_extended(self):
        """Retrun True if an extension has been called on the current hand."""
        with _game_exceptions():
            return self._game.current_hand.is_extended

    @property
    def is_small_deck(self):
        """Returns True if a small deck is being used (i.e. a 2-player game)."""
        return self._game.current_hand.is_small_deck

    @property
    def cards_remaining(self):
        """Returns the number of cards left in the deck."""
        return self._game.current_hand.cards_remaining

    @property
    def top_discarded_card(self):
        """Returns the top card on the discarded pile.

        Note: It does not remove the card from the pile. It just peeks at it.
        """
        with _game_exceptions():
            return self._game.current_hand.top_discarded_card

    @property
    def current_player_id(self):
        """Returns the id of the player who's turn it is."""
        with _game_exceptions():
            return self._game.current_hand.current_player_id

    @property
    def hand_winner_id(self):
        """Returns the id of the player that won the most recent hand."""
        return self._game.current_hand.winner_id

    def get_player_state(self, player_id=None):
        """Returns the state data for the given player.

        If player_id is None, the current player is used.
        """
        with _game_exceptions():
            return self._game.current_hand.get_player_state(player_id)

    def draw(self, player_id=None):
        """Draw a card.

        If player_id is None, the current player is used.
        """
        with _game_exceptions():
            return self._game.current_hand.draw(player_id)

    def draw_from_discard(self, player_id=None):
        """Draw a card from the discard pile.

        If player_id is None, the current player is used.
        """
        with _game_exceptions():
            return self._game.current_hand.draw_from_discard(player_id)

    def play(self, card_index, target_id=None, player_id=None):
        """Play a card.

        If player_id is None, the current player is used.
        target_id is only used for hazards.
        If target_id is None, and this is a 2-player game, then the other player is
        automatically the target.
        """
        with _game_exceptions():
            return self._game.current_hand.play(card_index, target_id, player_id)

    def discard(self, card_index, player_id=None):
        """Discard a card

        If player_id is None, the current player is used.
        """
        with _game_exceptions():
            return self._game.current_hand.discard(card_index, player_id)

    def coup_fourre(self, safety_index, player_id=None):
        """Trigger a Coup Fourré.

        player_id is the player doing the coup fourré.
        If player_id is None, the current player is used.
        """
        with _game_exceptions():
            return self._game.current_hand.coup_fourre(safety_index, player_id)

    def extension(self, winner_id=None):
        """Trigger an extension on the current hand.

        winner_id is the player that just won and has the option to extend.
        """
        with _game_exceptions():
            return self._game.current_hand.extension(winner_id)

    def get_player_scores(self):
        """Return the scores of all the players."""
        return self._game.current_hand.get_player_scores()

    def next_hand(self):
        """Starts the next hand of the game."""
        with _game_exceptions():
            self._game.new_hand()
