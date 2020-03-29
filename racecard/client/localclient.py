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


"""Race Card client implementation for running locally without a network."""


from collections import namedtuple
from contextlib import contextmanager

from racecard.client import base
from racecard.server import base as serverbase, localserver


Player = namedtuple("Player", "name id")


class LocalClientError(base.ClientError):
    """Exception class for all LocalClient errors."""


@contextmanager
def _server_exceptions():
    """Conext manager for handling server errors.

    Server exceptions are encapsulated as LocalClientError exceptions.
    """
    try:
        yield
    except serverbase.ServerError as error:
        raise LocalClientError(str(error)) from error


class LocalClient(base.ClientBase):
    """A Race Card client with embedded server for local (non-network) gameplay."""

    def __init__(self, server=None):
        self.players = {}
        self._server = server if server else localserver.LocalServer()

    @property
    def current_player(self):
        """Returns the player who's turn it is."""
        with _server_exceptions():
            return self.players[self._server.current_player_id]

    @property
    def is_small_deck(self):
        """Returns True if a small deck is being used (i.e. a 2-player game)."""
        return self._server.is_small_deck

    @property
    def hand_number(self):
        """Return the number of the current hand."""
        with _server_exceptions():
            return self._server.hand_number

    @property
    def round_number(self):
        """Return the number of the current round."""
        with _server_exceptions():
            return self._server.round_number

    @property
    def is_hand_completed(self):
        """Return True is the current hand has completed."""
        with _server_exceptions():
            return self._server.is_hand_completed

    @property
    def is_hand_extended(self):
        """Retrun True if an extension has been called on the current hand."""
        with _server_exceptions():
            return self._server.is_hand_extended

    @property
    def cards_remaining(self):
        """Returns the number of cards left in the deck."""
        return self._server.cards_remaining

    @property
    def top_discarded_card(self):
        """Returns the top card on the discarded pile.

        Note: It does not remove the card from the pile. It just peeks at it.
        """
        with _server_exceptions():
            return self._server.top_discarded_card

    def add_player(self, name):
        """Add a player to the game with the given name."""
        new_id = self._server.add_player()
        new_player = Player(name, new_id)
        self.players[new_id] = new_player
        return new_player

    def start_game(self):
        """Start the game."""
        with _server_exceptions():
            self._server.start_game()

    def get_player_state(self, player_id=None):
        """Returns the state data for the given player.

        If player_id is None, the current player is used.
        """
        with _server_exceptions():
            return self._server.get_player_state(player_id)

    def draw(self, player_id=None):
        """Draw a card.

        If player_id is None, the current player is used.
        """
        with _server_exceptions():
            return self._server.draw(player_id)

    def draw_from_discard(self, player_id=None):
        """Draw a card from the discard pile.

        If player_id is None, the current player is used.
        """
        with _server_exceptions():
            return self._server.draw_from_discard(player_id)

    def play(self, card_index, target_id=None, player_id=None):
        """Play a card.

        If player_id is None, the current player is used.
        target_id is only used for hazards.
        If target_id is None, and this is a 2-player game, then the other player is
        automatically the target.
        """
        with _server_exceptions():
            return self._server.play(card_index, target_id, player_id)

    def discard(self, card_index, player_id=None):
        """Discard a card

        If player_id is None, the current player is used.
        """
        with _server_exceptions():
            return self._server.discard(card_index, player_id)

    def coup_fourre(self, safety_index, player_id=None):
        """Trigger a Coup Fourré.

        player_id is the player doing the coup fourré.
        If player_id is None, the current player is used.
        """
        with _server_exceptions():
            return self._server.coup_fourre(safety_index, player_id)

    def extension(self, winner_id=None):
        """Trigger an extension on the current hand.

        winner_id is the player that just won and has the option to extend.
        """
        with _server_exceptions():
            return self._server.extension(winner_id)

    def get_player_scores(self):
        """Return the scores of all the players."""
        return self._server.get_player_scores()
