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

import uuid

from racecard.core import game

from . import common, user  # pylint:disable=cyclic-import


class Game(common.ModelBase, game.Game):
    """A single game consisting of several hands, played by several players."""

    id: uuid.UUID
    owner: user.User

    def __init__(self, id, owner):  # pylint: disable=redefined-builtin
        super().__init__()
        self.id = id  # pylint: disable=invalid-name
        self.owner = owner