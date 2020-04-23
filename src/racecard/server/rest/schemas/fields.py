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


"""All correct schema fields are importable from here."""

# pylint: disable=wildcard-import,unused-wildcard-import,unused-import

import typing

import timeflake
from marshmallow.fields import *  # noqa: F403,F401
from marshmallow_jsonapi.fields import DocumentMeta, ResourceMeta  # noqa: F401
from marshmallow_jsonapi.flask import Relationship  # noqa: F401


# Copied / based on marshmallow.fields.UUID.
class Timeflake(String):  # noqa: F405
    """A Timeflake field."""

    default_error_messages = {"invalid_timeflake": "Not a valid Timeflake."}

    def _validated(self, value) -> typing.Optional[timeflake.Timeflake]:
        """Format the value or raise a :exc:`ValidationError` if an error occurs."""
        if value is None:
            return None
        if isinstance(value, timeflake.Timeflake):
            return value
        try:
            return timeflake.parse(from_base62=value)
        except (ValueError, AttributeError, TypeError) as error:
            raise self.make_error("invalid_timeflake") from error

    def _deserialize(
        self, value, attr, data, **kwargs
    ) -> typing.Optional[timeflake.Timeflake]:
        return self._validated(value)
