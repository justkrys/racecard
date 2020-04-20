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


def load_dummy_data():
    """Loads dummy data."""
    krys = user.User(
        id=uuid.UUID("90c6058e-5982-4e8c-85d5-40cd7251faad"),
        name="Krys",
        email="krys@example.com",
    )
    users[krys.id] = krys
    cheesebutt = user.User(
        id=uuid.UUID("57eea3c9-b699-4f99-82a3-f44f2307ec2b"),
        name="Cheesebutt",
        email="cheesebutt@example.com",
    )
    users[cheesebutt.id] = cheesebutt
    krys_game = game.Game(
        id_=uuid.UUID("864c5ff8-9883-4494-b76f-2d5365e37a6c"), owner=krys
    )
    games[krys_game.id] = krys_game
    cheesebutt_game = game.Game(
        id_=uuid.UUID("2e343883-6983-4d06-a23d-c6da97764e06"), owner=cheesebutt
    )
    games[cheesebutt_game.id] = cheesebutt_game


if os.environ.get("RACECARD_DEV", "").lower() == "true":
    load_dummy_data()
