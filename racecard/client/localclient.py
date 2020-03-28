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


from collections import namedtuple
from contextlib import contextmanager

from racecard.client import base
from racecard.server import base as serverbase, localserver


Player = namedtuple('Player', 'name id')


class LocalClientError(base.ClientError):
    pass


@contextmanager
def _server_exceptions():
    try:
        yield
    except serverbase.ServerError as error:
        raise LocalClientError(str(error)) from error


class LocalClient(base.ClientBase):

    def __init__(self, server=None):
        self.players = {}
        self._server = (server if server else localserver.LocalServer())

    @property
    def current_player(self):
        with _server_exceptions():
            return self.players[self._server.current_player_id]

    @property
    def is_small_deck(self):
        return self._server.is_small_deck

    @property
    def hand_number(self):
        with _server_exceptions():
            return self._server.hand_number

    @property
    def round_number(self):
        with _server_exceptions():
            return self._server.round_number

    @property
    def is_hand_completed(self):
        with _server_exceptions():
            return self._server.is_hand_completed

    @property
    def is_hand_extended(self):
        with _server_exceptions():
            return self._server.is_hand_extended

    @property
    def cards_remaining(self):
        return self._server.cards_remaining

    @property
    def top_discarded_card(self):
        with _server_exceptions():
            return self._server.top_discarded_card

    def add_player(self, name):
        new_id = self._server.add_player()
        new_player = Player(name, new_id)
        self.players[new_id] = new_player
        return new_player

    def start_game(self):
        with _server_exceptions():
            self._server.start_game()

    def get_player_state(self, player_id=None):
        with _server_exceptions():
            return self._server.get_player_state(player_id)

    def draw(self, player_id=None):
        with _server_exceptions():
            return self._server.draw(player_id)

    def draw_from_discard(self, player_id=None):
        with _server_exceptions():
            return self._server.draw_from_discard(player_id)

    def play(self, card_index, target_id=None, player_id=None):
        with _server_exceptions():
            return self._server.play(card_index, target_id, player_id)

    def discard(self, card_index, player_id=None):
        with _server_exceptions():
            return self._server.discard(card_index, player_id)

    def coup_fourre(self, safety_index, player_id=None):
        with _server_exceptions():
            return self._server.coup_fourre(safety_index, player_id)

    def extension(self, winner_id=None):
        with _server_exceptions():
            return self._server.extension(winner_id)

    def get_player_scores(self):
        return self._server.player_scores()
