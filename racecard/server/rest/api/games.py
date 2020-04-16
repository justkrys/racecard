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


from flask import url_for

from racecard.server.rest import store


def search():
    """Returns the list of all games that currently exist.

    Implements GET on /games.

    Currently does not support searching or filtering.
    """
    games = list(store.games) + ["1234"]
    result = dict(
        jsonapi=dict(version="1.0"),
        data=[],
        meta=dict(count=len(games)),
        links=dict(self=url_for(".games_search")),
    )
    for game_id in games:
        result["data"].append(
            dict(
                id=game_id,
                type="game",
                links=dict(self=url_for(".games_search") + f"/{game_id}"),
            )
        )
    return result, 200, {"Content-Type": "application/vnd.api+json"}
