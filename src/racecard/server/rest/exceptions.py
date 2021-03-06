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

from ...core import exceptions as coreexceptions
from .. import common as servercommon
from .models import common as modelscommon
from .schemas import common as schemascommon


class RESTAppException(servercommon.ServerError):
    """Base class for all REST server exceptions."""

    message: typing.Optional[str] = None
    id_: modelscommon.ID
    status: int = 500
    code: typing.Optional[str] = None
    detail: typing.Optional[str] = None
    pointer: typing.Optional[str] = None
    parameter: typing.Optional[str] = None
    schema_class: typing.Type[schemascommon.Schema]

    def __init__(
        self,
        id_: modelscommon.ID,
        schema_class: typing.Type[schemascommon.Schema] = None,
        *,
        detail: str = None,
        pointer: str = None,
        parameter: str = None
    ):
        # Not supporting instance-level messages because we are mapping message to
        # title in the JSON:API output and title is specified as not changing for all
        # occurances of the error type.
        # So, message should be set at the class level.  If not specified, the class
        # docstring will be used.
        super().__init__()
        self.id_ = id_
        if schema_class is not None:
            self.schema_class = schema_class
        if detail is not None:
            self.detail = detail
        if pointer is not None:
            self.pointer = pointer
        if parameter is not None:
            self.parameter = parameter


class NotFoundError(RESTAppException):
    """Resource not found."""

    status = 404
    parameter = "id"


class CoreError(RESTAppException):
    """Wraps core exceptions so that they can be returned to clients."""

    status = 400

    def __init__(self, error: coreexceptions.CoreException, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = error.__class__.__name__
        self.message = str(error)
        self.original_error = error
