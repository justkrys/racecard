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


"""Common utilities for resources."""


import functools
import inspect
import uuid

from ..models import common


def document(doc, code=200):
    """Returns document and code, but with content type set to JSON:API."""
    return doc, code, {"Content-Type": "application/vnd.api+json"}


def single(data, schema_or_class, code=200):
    """Returns data and code, but with content type set to JSON:API.

    Converts data to a JSON:API document using the given schema.
    schema can be a Schema class or an instance of it.
    """
    schema = schema_or_class() if isinstance(schema_or_class, type) else schema_or_class
    doc = schema.dump(data)
    return document(doc, code)


def many(data, schema_class, code=200, include_data=None, **collectionmeta_kwargs):
    """Returns collection data and code, but with content type set to JSON:API.

    Converts collection data using the given schema class.
    Includes CollectionMeta data model as document meta data.
    Any extra keyword arguments are passed to CollectionMeta.
    If no total is given for CollectionMeta, it is calculated as len(data) and included
    automatically.
    """
    if collectionmeta_kwargs.get("total", None) is None:
        collectionmeta_kwargs["total"] = len(data)
    meta = common.CollectionMeta(**collectionmeta_kwargs)
    schema = schema_class(document_meta=meta, include_data=include_data)
    doc = schema.dump(data, many=True)
    return document(doc, code)


def id_is_uuid(func):
    """Decorator to automatically convert "id" or "id_" argument from string to UUID."""
    # Pre-calculate as much as possible to keep actual invocation quick.
    P = inspect.Parameter
    parameters = inspect.signature(func).parameters
    id_keys = [key for key in parameters if key in ("id", "id_")]
    if not id_keys:
        return func
    key = id_keys[0]
    parameter = parameters[key]
    is_keyword = parameter.kind in (P.KEYWORD_ONLY, P.POSITIONAL_OR_KEYWORD)
    is_positional = parameter.kind in (P.POSITIONAL_ONLY, P.POSITIONAL_OR_KEYWORD)
    if is_positional:
        index = list(parameters).index(key)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if is_keyword and key in kwargs:
            kwargs[key] = uuid.UUID(kwargs[key])
        elif is_positional and len(args) > index:
            args = list(args)
            args[index] = uuid.UUID(args[index])
        return func(*args, **kwargs)

    return wrapper
