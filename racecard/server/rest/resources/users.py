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

from .. import store
from ..models import common, user
from ..schemas import userschema
from .common import j


def search():
    """Handler for GET /users."""
    users = list(store.users.values())
    a_user = user.User(id=uuid.uuid4(), name="bob", email="bob@bob")
    users.append(a_user)
    meta = common.CollectionMeta(total=len(users), page=1, page_size=20, total_pages=4)
    schema = userschema.UserSchema(document_meta=meta)
    doc = schema.dump(users, many=True)
    return j(doc)


def get(id):  # pylint: disable=invalid-name,redefined-builtin
    """Handler for GET /users/<id>."""
    # user = store.users[id]
    user_ = user.User(id=id, name="bob", email="bob@bob")
    schema = userschema.UserSchema()
    doc = schema.dump(user_)
    return j(doc)
