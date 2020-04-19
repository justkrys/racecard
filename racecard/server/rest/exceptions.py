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


"""REST server exceptions and handling."""


import typing

from .. import common as servercommon
from .schemas import common as schemascommon


class RESTAppException(servercommon.ServerError):
    """Base class for all REST server exceptions."""

    message = None
    id_: str
    status: int = 500
    detail: typing.Union[str, None] = None
    pointer: typing.Union[str, None] = None
    parameter: typing.Union[str, None] = None
    schema_class: typing.Type[schemascommon.ErrorSchema] = schemascommon.ErrorSchema

    def __init__(self, id_, *, detail=None, pointer=None, parameter=None):
        # Not supporting instance-level messages because we are mapping message to
        # title in the JSON:API output and title is specified as not changing for all
        # occurances of the error type.
        # So, message should be set at the class level.  If not specified, the class
        # docstring will be used.
        super().__init__()
        self.id_ = id_
        if detail is not None:
            self.detail = detail
        if pointer is not None:
            self.pointer = pointer
        if parameter is not None:
            self.parameter = parameter
