
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
