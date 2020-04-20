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

import uuid

from .. import exceptions, store
from ..schemas import gameschema, userschema
from . import common


def search():
    """Handler for GET /users."""
    data = list(store.users.values())
    return common.many(data, userschema.UserSchema)


def get(id):  # pylint: disable=invalid-name,redefined-builtin
    """Handler for GET /users/<id>."""
    try:
        data = store.users[uuid.UUID(id)]
    except KeyError:
        raise exceptions.NotFoundError(id, userschema.UserSchema)
    return common.single(data, userschema.UserSchema)


def get_owned(id):  # pylint: disable=invalid-name,redefined-builtin
    """Handler for GET /users/<id>/owned."""
    try:
        data = store.users[uuid.UUID(id)].owned
    except KeyError:
        raise exceptions.NotFoundError(id, userschema.UserSchema)
    # FIXME: self link is inaccurate when using GameSchema directly like this.
    return common.many(data, gameschema.GameSchema)
