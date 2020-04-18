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


"""Data model for users."""

import dataclasses
import typing
import uuid

from . import common


@dataclasses.dataclass
class User(common.ModelBase):
    """A single game consisting of several hands, played by several players."""

    id: uuid.UUID  # pylint: disable=invalid-name
    name: str
    email: str
    owned: typing.AbstractSet[uuid.UUID] = dataclasses.field(default_factory=set)
    playing: typing.AbstractSet[uuid.UUID] = dataclasses.field(default_factory=set)
    completed: typing.AbstractSet[uuid.UUID] = dataclasses.field(default_factory=set)
