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


"""Top-level of core.  The Game class runs a whole game."""


import random
import uuid

from racecard.core import exceptions, hand


class Game:
    """Top-level Game class.  Registers players and runs multiple hands.

    Servers/applications should instantiate this class.
    """

    def __init__(self):
        self.player_ids = []
        self.turn_order = []
        self.hands = []

    # @property
    # def is_running(self):
    #     # No hands, not running (game not started).
    #     # Have hands, but last hand is completed, also not running (game finished)
    #     return bool(self.hands) and not self.current_hand.is_completed

    @property
    def current_hand(self):
        """Returns the current hand object."""
        try:
            return self.hands[-1]
        except IndexError:
            raise exceptions.NotBegunError()

    def join(self):
        """Adds a new player to the game and retruns their id."""
        new_id = uuid.uuid4()
        self.player_ids.append(new_id)
        return new_id

    def begin(self):
        """Begin the game or InsufficientPlayersError if not enough players."""
        if len(self.player_ids) < 2:
            raise exceptions.InsufficientPlayersError()
        self.turn_order = self.player_ids.copy()
        random.shuffle(self.turn_order)  # Shuffle is an in-place operation!
        self.new_hand()

    def new_hand(self):
        """Creates a new hand or HandInProgressError if current one is still going."""
        if self.hands and not self.current_hand.is_completed:
            raise exceptions.HandInProgressError()
        self.hands.append(hand.Hand(len(self.hands) + 1, self.turn_order))
