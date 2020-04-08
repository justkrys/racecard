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

# Base Classes


class ExceptionBase(Exception):
    """Base class for all Race Card exceptions.

    Includes support for default messages and using doctstrings as messages.
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


# General Exceptions


class HandInProgressError(CoreException):
    """Hand is still in progress!"""


class HandCompletedError(CoreException):
    """Hand is completed!"""


class CannotCoupFourreError(CoreException):
    """Cannot Coup Fourré at this time!"""


# Player Exceptions


class InvalidCardIndexError(CoreException):
    """Invalid card index!"""


class InvalidCardError(CoreException):
    """Invalid card!"""


class InvalidPlayError(CoreException):
    """Cannot play card at this time!"""


class DiscardSafetyWarning(CoreException):
    """Do not discard Safety cards!"""


# Tray Exceptions


class EmptyPileError(CoreException):
    """Draw or Discard pile is empty."""

    def __init__(self, draw=False):
        message = ("Draw" if draw else "Discard") + " pile is empty!"
        super().__init__(message)


# Hand Exceptions


class InvalidPlayerError(CoreException):
    """Invalid player!"""


class InvalidTargetError(CoreException):
    """Invalid target player!"""


class OutOfTurnError(CoreException):
    """Not your turn!"""


class MustDrawError(CoreException):
    """Must draw a card first!"""


class CannotDrawError(CoreException):
    """Cannot draw another card!"""


class CannotExtendError(CoreException):
    """Cannot call an extension!"""


# Game Exceptions


class InsufficientPlayersError(CoreException):
    """Not enough player have joined this game!"""


class NotBegunError(CoreException):
    """Game has not yet begun!"""


class TooManyPlayers(CoreException):
    """Too many players!  Max player count already met."""
