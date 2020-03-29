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


"""Core error types and base classes for all Race Card exceptions."""


class ExceptionBase(Exception):
    """Base class for all Race Card exceptions.

    Includes support for default messages.
    """

    message = None

    def __init__(self, message=None):
        if message is None:
            if self.message is not None:
                # Support for a default message.
                message = self.message
            elif self.__class__.__doc__ is not None:
                # Support use of class docstring as default message.
                message = self.__class__.__doc__
        super().__init__(message)


class CoreException(ExceptionBase):
    """Base class for all core exceptions."""


# Game Exceptions


class GameError(CoreException):
    """Base class for all Game exceptions."""


class NotBegunError(GameError):
    """Game has not yet begun!"""


class InsufficientPlayersError(GameError):
    """Not enough player have joined this game!"""


# Hand Exceptions


class HandError(CoreException):
    """Base class for all Hand exceptions."""


class InvalidPlayerError(HandError):
    """Invalid player ID!"""


class MustDrawError(HandError):
    """Must draw a card first!"""


class AlreadyDrawnError(HandError):
    """Already drawn, cannot draw again!"""


class AmbiguousTargetError(HandError):
    """Multiple target choices, a target player must be specified!"""


class PreventedBySafetyError(HandError):
    """Play prevented by safety!"""


class InvalidPlayError(HandError):
    """Cannot play card at this time!"""


class OutOfTurnError(HandError):
    """Not your turn!"""


class InvalidCardIndexError(HandError):
    """Invalid card index!"""


class InvalidTargetError(HandError):
    """Card cannot be played on another player!"""


class HandInProgressError(HandError):
    """Hand is still in progress!"""


class ExtensionNotAllowedError(HandError):
    """Extension is not allowed!"""


class AlreadyExtendedError(HandError):
    """Has is already extended!"""


class HandCompletedError(HandError):
    """Hand is completed, no further plays allowed!"""


# Tray Exceptions


class EmptyPileError(CoreException):
    """Draw or Discard pile is empty."""

    def __init__(self, draw=False):
        message = ("Draw" if draw else "Discard") + " pile is empty!"
        super().__init__(message)
        self.draw = draw
