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


"""Data model for Race Card games."""


from __future__ import annotations  # Solve circular type references with user.

import functools
import typing
import uuid

from ....core import exceptions as coreexceptions
from ....core import game as coregame
from .. import exceptions
from ..schemas import gameschema
from . import common, user  # pylint:disable=cyclic-import


def _raises_core_exceptions(method):
    """Decorator to handle converting core exceptions."""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except coreexceptions.CoreException as error:
            raise exceptions.CoreError(error, self.id, self.__schema__)

    return wrapper


class Game(common.ModelBase):
    """A single game consisting of several hands, played by several players."""

    __schema__ = gameschema.GameSchema
    id: common.ID
    owner: user.User
    players: typing.MutableSequence[user.User]

    def __init__(
        self, id: common.ID, owner: user.User
    ):  # pylint: disable=redefined-builtin
        super().__init__()
        self._game = coregame.Game()
        # Map user ids to internal player ids.
        self._player_map: typing.Dict[common.ID, uuid.UUID] = {}
        self.id = id  # pylint: disable=invalid-name
        self.owner = owner
        self.players = []

    @property
    def is_completed(self):
        """Returns True if the game is completed."""
        return self._game.is_completed

    @_raises_core_exceptions
    def add_player(self, player: user.User):
        """Adds the given player to the game."""
        player_id = self._game.add_player()
        self.players.append(player)
        self._player_map[player.id] = player_id
