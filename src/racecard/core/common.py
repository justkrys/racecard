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


"""Common/utility code for the core package."""


import enum


class _Enum(enum.Enum):
    """Enum that makes members values the same as member names.

    Also their str output is just their plain name/value as well.
    """

    @staticmethod
    def _generate_next_value_(
        name, start, count, last_values
    ):  # pylint: disable=unused-argument
        return name

    def __str__(self):
        return self.value


def Enum(*args, **kwargs):  # pylint: disable=invalid-name
    """Creates an Enum class with member values and str outputs as only their names."""
    return enum.unique(_Enum(*args, **kwargs))
