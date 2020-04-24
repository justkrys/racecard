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

from . import exceptions
from .models import common as modelscommon
from .models import game as gamemodel
from .models import user as usermodel

games: typing.Dict[modelscommon.ID, gamemodel.Game] = {}
users: typing.Dict[modelscommon.ID, usermodel.User] = {}


def load_dummy_data() -> None:
    """Loads dummy data."""
    krys = usermodel.User(
        id=modelscommon.ID.parse("02ivWdgcJ6uB0sdvq8ZqA5"),
        name="Krys",
        email="krys@example.com",
    )
    users[krys.id] = krys
    cheesebutt = usermodel.User(
        id=modelscommon.ID.parse("02ivWfqYf0alI2UxQw3AZU"),
        name="Cheesebutt",
        email="cheesebutt@example.com",
    )
    users[cheesebutt.id] = cheesebutt
    krys_game = gamemodel.Game(
        id=modelscommon.ID.parse("02ivWgA7Lz8eWuI313ix0w"), owner=krys
    )
    games[krys_game.id] = krys_game
    cheesebutt_game = gamemodel.Game(
        id=modelscommon.ID.parse("02ivWgB8W6JaY1BpwbE28g"), owner=cheesebutt
    )
    games[cheesebutt_game.id] = cheesebutt_game
    krys_game.add_player(krys)
    krys_game.add_player(cheesebutt)
    cheesebutt_game.add_player(krys)
    cheesebutt_game.add_player(cheesebutt)


if os.environ.get("RACECARD_DEV", "").lower() == "true":
    load_dummy_data()


def find_users(
    *, game: typing.Union[gamemodel.Game, modelscommon.ID] = None
) -> typing.Iterable[usermodel.User]:
    """Returns users that match the given criteria."""
    matches = list(users.values())
    if game is not None:
        if isinstance(game, modelscommon.ID):
            game = get_game(game)
        matches = [
            user for user in matches if user == game.owner or user in game.players
        ]
    return matches


def get_user(id_: modelscommon.ID) -> usermodel.User:
    """Returns the user that matches either the id or the email."""
    if id_ in users:
        return users[id_]
    raise exceptions.NotFoundError(id_)


def find_games(
    *,
    owner: typing.Union[usermodel.User, modelscommon.ID] = None,
    player: typing.Union[usermodel.User, modelscommon.ID] = None,
    state: str = None,
) -> typing.Iterable[gamemodel.Game]:
    """Returns games that match the given criteria."""
    matches = list(games.values())
    if owner is not None:
        if isinstance(owner, modelscommon.ID):
            owner = get_user(owner)
        matches = [game_ for game_ in matches if game_.owner == owner]
    if player is not None:
        if isinstance(player, modelscommon.ID):
            player = get_user(player)
        matches = [game_ for game_ in matches if player in game_.players]
    if state is not None:
        valid_states = ("notstarted", "running", "completed")
        if state not in valid_states:
            raise ValueError(f"state must be one of {str(valid_states)}.")
        # TODO: Implement support for remaining game filtering.
        if state == "notstarted":
            raise NotImplementedError()
        elif state == "running":
            raise NotImplementedError()
        elif state == "completed":
            matches = [game for game in matches if game.is_completed]
    return matches


def get_game(id_: modelscommon.ID) -> gamemodel.Game:
    """Returns the game that matches the given id."""
    if id_ in games:
        return games[id_]
    raise exceptions.NotFoundError(id_)
