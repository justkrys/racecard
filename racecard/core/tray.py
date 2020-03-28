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


from racecard.core import exceptions


class Tray:

    def __init__(self, deck):
        # NOTE: The top of each of these piles is the last entry in the list.  Tail = top, head = bottom.
        self._draw_pile = deck
        self._discard_pile = []

    @property
    def cards_remaining(self):
        return len(self._draw_pile)

    def draw(self):
        try:
            return self._draw_pile.pop()
        except IndexError:
            raise exceptions.EmptyPileError(draw=True)

    def discard(self, card):
        self._discard_pile.append(card)

    def draw_from_discard(self):
        try:
            return self._discard_pile.pop()
        except IndexError:
            raise exceptions.EmptyPileError()

    @property
    def top_discarded_card(self):
        try:
            return self._discard_pile[-1]
        except IndexError:
            raise exceptions.EmptyPileError()

    @property
    def is_draw_pile_empty(self):
        return bool(self._draw_pile)
