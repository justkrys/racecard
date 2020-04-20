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
        id=uuid.UUID("864c5ff8-9883-4494-b76f-2d5365e37a6c"), owner=krys
    )
    games[krys_game.id] = krys_game
    cheesebutt_game = game.Game(
        id=uuid.UUID("2e343883-6983-4d06-a23d-c6da97764e06"), owner=cheesebutt
    )
    games[cheesebutt_game.id] = cheesebutt_game


if os.environ.get("RACECARD_DEV", "").lower() == "true":
    load_dummy_data()


def find_users(*, name=None):
    """Returns users that match the given criteria."""
    matches = users.values()
    if name is not None:
        matches = [user for user in matches if user.name.lower() == name.lower()]
    return matches


def get_user(id_=None, email=None):
    """Returns the user that matches either the id or the email."""
    if id_ is None and email is None:
        raise TypeError("At least one argument must be provided.")
    if id_ is not None:
        if not isinstance(id, uuid.UUID):
            id_ = uuid.UUID(id_)
        return users[id_]
    return [user for user in users if user.email.lower() == email.lower()][0]


def find_games(*, owner_id=None, player_id=None, state=None):
    """Returns games that match the given criteria."""
    matches = games.values()
    if owner_id is not None:
        if not isinstance(owner_id, uuid.UUID):
            owner_id = uuid.UUID(owner_id)
        matches = [game for game in matches if game.owner.id == owner_id]
    # TODO: Implement support for remaining game filtering.
    if player_id is not None:
        if not isinstance(player_id, uuid.UUID):
            player_id = uuid.UUID(player_id)
        raise NotImplementedError()
    if state is not None:
        valid_states = ("notstarted", "running", "completed")
        if state not in valid_states:
            raise ValueError(f"state must be one of {str(valid_states)}.")
        if state == "notstarted":
            raise NotImplementedError()
        elif state == "running":
            raise NotImplementedError()
        elif state == "completed":
            matches = [game for game in matches if game.is_completed]
    return matches


def get_game(id_):
    """Returns the game that matches the given id."""
    if not isinstance(id_, uuid.UUID):
        id_ = uuid.UUID(id_)
    return games[id_]
