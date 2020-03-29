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


class ExceptionBase(Exception):

    message = None

    def __init__(self, message=None):
        if message is None:
            if self.message is not None:
                # Support for a default message.
                message = self.message
        super().__init__(message)


class CoreException(ExceptionBase):
    pass


# Game Exceptions


class GameError(CoreException):
    pass


class NotBegunError(GameError):
    message = "Game has not yet begun!"


class InsufficientPlayersError(GameError):
    message = "Not enough player have joined this game!"


# Hand Exceptions


class HandError(CoreException):
    pass


class InvalidPlayerError(HandError):
    message = "Invalid player ID!"


class MustDrawError(HandError):
    message = "Must draw a card first!"


class AlreadyDrawnError(HandError):
    message = "Already drawn, cannot draw again!"


class AmbiguousTargetError(HandError):
    message = "Multiple target choices, a target player must be specified!"


class PreventedBySafetyError(HandError):
    message = "Play prevented by safety!"


class InvalidPlayError(HandError):
    message = "Cannot play card at this time!"


class OutOfTurnError(HandError):
    message = "Not your turn!"


class InvalidCardIndexError(HandError):
    message = "Invalid card index!"


class InvalidTargetError(HandError):
    message = "Card cannot be played on another player!"


class HandInProgressError(HandError):
    message = "Hand is still in progress!"


class ExtensionNotAllowedError(HandError):
    message = "Extension is not allowed!"


class AlreadyExtendedError(HandError):
    message = "Has is already extended!"


class HandCompletedError(HandError):
    message = "Hand is completed, no further plays allowed!"


# Tray Exceptions


class EmptyPileError(CoreException):
    def __init__(self, draw=False):
        message = ("Draw" if draw else "Discard") + " pile is empty!"
        super().__init__(message)
        self.draw = draw
