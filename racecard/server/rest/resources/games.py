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


"""API for game resources."""


import flask

from .. import store
from . import common


def search():
    """Returns the list of all games that currently exist.

    Implements GET on /games.

    Currently does not support searching or filtering.
    """
    games = list(store.games)
    doc = dict(
        jsonapi=dict(version="1.0"),
        data=[],
        meta=dict(total=len(games)),
        links=dict(self=flask.url_for(".games_search")),
    )
    for game_id in games:
        doc["data"].append(
            dict(
                type="game",
                id=game_id,
                links=dict(self=flask.url_for(".games_search") + f"/{game_id}"),
            )
        )
    return common.document(doc)
