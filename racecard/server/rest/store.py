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


"""In-memory storage of global state.

This serves as a temporary substitute for an actualy db or storage backend.
"""


import os
import typing
import uuid

from .models import game, user

games: typing.Dict[uuid.UUID, game.Game] = {}
users: typing.Dict[uuid.UUID, user.User] = {}

if os.environ.get("RACECARD_DEV", "").lower() == "true":
    for name in ("Krys", "Cheesebutt"):
        id_ = uuid.uuid4()
        users[id_] = user.User(id=id_, name=name, email=f"{name.lower()}@example.com")
