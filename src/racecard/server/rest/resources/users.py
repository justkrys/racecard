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


"""API for user resources."""

from .. import exceptions, store
from ..schemas import userschema
from . import common


@common.id_kwargs("game")
def search(game=None):
    """Handler for GET /users."""
    try:
        data = store.find_users(game=game)
    except exceptions.NotFoundError as error:
        error.schema_class = userschema.UserSchema
        raise
    return common.many(data, userschema.UserSchema)


@common.id_kwargs("id_")
def get(id_):
    """Handler for GET /users/<id>."""
    try:
        data = store.get_user(id_)
    except exceptions.NotFoundError as error:
        error.schema_class = userschema.UserSchema
        raise
    return common.single(data, userschema.UserSchema)
