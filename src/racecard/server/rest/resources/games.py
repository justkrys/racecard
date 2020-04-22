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

import uuid

from .. import exceptions, store
from ..schemas import gameschema
from . import common


def search(*, owner=None, player=None, state=None):
    """Handler for GET /games."""
    if owner is not None:
        owner = uuid.UUID(owner)
    if player is not None:
        player = uuid.UUID(player)
    games = store.find_games(owner_id=owner, player_id=player, state=state)
    return common.many(games, gameschema.GameSchema)


@common.id_is_uuid
def get(id_):
    """Handler for GET /games/<id>."""
    try:
        game = store.get_game(id_)
    except exceptions.NotFoundError as error:
        error.schema_class = gameschema.GameSchema
        raise
    return common.single(game, gameschema.GameSchema)
