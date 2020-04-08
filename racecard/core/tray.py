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


"""Tracks cards in the draw and discard piles."""


from racecard.core import exceptions


class Tray:
    """The tray contains all the cards in the draw and discard piles."""

    def __init__(self, deck):
        # NOTE: The top of each of these piles is the last entry in the list.
        #       Tail = top, head = bottom.
        self._draw_pile = deck
        self._discard_pile = []

    @property
    def cards_remaining(self):
        """Returns the number of cards remaining in the draw pile."""
        return len(self._draw_pile)

    @property
    def top_discarded_card(self):
        """Returns the top card on the discard pile or EmptyPileError is none exists.

        Does not remove the card from the pile, it just peeks at it.
        """
        try:
            return self._discard_pile[-1]
        except IndexError:
            raise exceptions.EmptyPileError()

    def draw(self, discard=False):
        """Draw one card from the top of either the draw or discard pile and return it.

        The card is removed from the pile, and the one under it becomes the new top
        card.
        """
        pile = self._draw_pile if not discard else self._discard_pile
        try:
            return pile.pop()
        except IndexError:
            raise exceptions.EmptyPileError(draw=True)

    def discard(self, card):
        """Discard one card to the discard pile.

        The card is added to the top of the discard pile.
        """
        self._discard_pile.append(card)
