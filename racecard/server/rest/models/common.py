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


"""Common utilities for data models."""


import dataclasses
import typing


class ModelBase:  # pylint: disable=too-few-public-methods
    """Base class for all Race Card data models."""


@dataclasses.dataclass
class CollectionMeta:  # pylint: disable=too-few-public-methods
    """Common meta-data attributes to add to collections of resources.

    These would go in the document-level "meta" attribute in JSON:API, for example.
    """

    total: int
    page: typing.Union[int, None] = None
    page_size: typing.Union[int, None] = None
    total_pages: typing.Union[int, None] = None


@dataclasses.dataclass
class ErrorSource:
    """Data model for describing appication error sources in JSON:API format.

    At least one of the two attributes should be specified.
    """

    pointer: typing.Union[str, None] = None
    parameter: typing.Union[str, None] = None


@dataclasses.dataclass
class Error(ModelBase):
    """Data model for describing applicaion errors in JSON:API format."""

    id: str  # pylint: disable=invalid-name
    status: str
    code: str
    title: str
    detail: typing.Union[str, None] = None
    source: typing.Union[ErrorSource, None] = None
