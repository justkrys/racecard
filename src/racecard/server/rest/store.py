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

import timeflake

from . import exceptions
from .models import game, user

games: typing.Dict[timeflake.Timeflake, game.Game] = {}
users: typing.Dict[timeflake.Timeflake, user.User] = {}


def load_dummy_data() -> None:
    """Loads dummy data."""
    krys = user.User(
        id=timeflake.parse(from_base62="02ivWdgcJ6uB0sdvq8ZqA5"),
        name="Krys",
        email="krys@example.com",
    )
    users[krys.id] = krys
    cheesebutt = user.User(
        id=timeflake.parse(from_base62="02ivWfqYf0alI2UxQw3AZU"),
        name="Cheesebutt",
        email="cheesebutt@example.com",
    )
    users[cheesebutt.id] = cheesebutt
    krys_game = game.Game(
        id=timeflake.parse(from_base62="02ivWgA7Lz8eWuI313ix0w"), owner=krys
    )
    games[krys_game.id] = krys_game
    cheesebutt_game = game.Game(
        id=timeflake.parse(from_base62="02ivWgB8W6JaY1BpwbE28g"), owner=cheesebutt
    )
    games[cheesebutt_game.id] = cheesebutt_game


if os.environ.get("RACECARD_DEV", "").lower() == "true":
    load_dummy_data()


def find_users(*, name: str = None) -> typing.Iterable[user.User]:
    """Returns users that match the given criteria."""
    matches = list(users.values())
    if name is not None:
        matches = [user for user in matches if user.name.lower() == name.lower()]
    return matches


def get_user(id_: timeflake.Timeflake = None, email: str = None) -> user.User:
    """Returns the user that matches either the id or the email."""
    if id_ is None and email is None:
        raise ValueError("At least one argument must be provided")
    if id_ is not None and id_ in users:
        return users[id_]
    if email is not None:
        for user_ in users.values():
            if user_.email.lower() == email.lower():
                return user_
    raise exceptions.NotFoundError(id_)


def find_games(
    *,
    owner_id: timeflake.Timeflake = None,
    player_id: timeflake.Timeflake = None,
    state: str = None,
) -> typing.Iterable[game.Game]:
    """Returns games that match the given criteria."""
    matches = list(games.values())
    if owner_id is not None:
        matches = [game_ for game_ in matches if game_.owner.id == owner_id]
    # TODO: Implement support for remaining game filtering.
    if player_id is not None:
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


def get_game(id_: timeflake.Timeflake) -> game.Game:
    """Returns the game that matches the given id."""
    if id_ in games:
        return games[id_]
    raise exceptions.NotFoundError(id)
