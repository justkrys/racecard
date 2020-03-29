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


from contextlib import contextmanager

from racecard.server import base
from racecard.core import game, exceptions


class LocalServerError(base.ServerError):
    pass


@contextmanager
def _game_exceptions():
    try:
        yield
    except exceptions.CoreException as error:
        raise LocalServerError(str(error)) from error


class LocalServer(base.ServerBase):
    def __init__(self):
        self._game = game.Game()

    # Game Methods

    def add_player(self):
        return self._game.join()

    def start_game(self):
        with _game_exceptions():
            self._game.begin()

    # Hand Methods

    @property
    def hand_number(self):
        with _game_exceptions():
            return self._game.current_hand.number

    @property
    def round_number(self):
        with _game_exceptions():
            return self._game.current_hand.round

    @property
    def is_hand_completed(self):
        with _game_exceptions():
            return self._game.current_hand.is_completed

    @property
    def is_hand_extended(self):
        with _game_exceptions():
            return self._game.current_hand.is_extended

    @property
    def is_small_deck(self):
        return self._game.current_hand.is_small_deck

    @property
    def cards_remaining(self):
        return self._game.current_hand.cards_remaining

    @property
    def top_discarded_card(self):
        with _game_exceptions():
            return self._game.current_hand.top_discarded_card

    @property
    def current_player_id(self):
        with _game_exceptions():
            return self._game.current_hand.current_player_id

    def get_player_state(self, player_id=None):
        with _game_exceptions():
            return self._game.current_hand.get_player_state(player_id)

    def draw(self, player_id=None):
        with _game_exceptions():
            return self._game.current_hand.draw(player_id)

    def draw_from_discard(self, player_id=None):
        with _game_exceptions():
            return self._game.current_hand.draw_from_discard(player_id)

    def play(self, card_index, target_id=None, player_id=None):
        with _game_exceptions():
            return self._game.current_hand.play(card_index, target_id, player_id)

    def discard(self, card_index, player_id=None):
        with _game_exceptions():
            return self._game.current_hand.discard(card_index, player_id)

    def coup_fourre(self, safety_index, player_id=None):
        with _game_exceptions():
            return self._game.current_hand.coup_fourre(safety_index, player_id)

    def extension(self, winner_id=None):
        with _game_exceptions():
            return self._game.current_hand.extension(winner_id)

    def get_player_scores(self):
        return self._game.current_hand.get_player_scores()
