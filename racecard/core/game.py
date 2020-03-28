
import random
import uuid

from racecard.core import exceptions, hand


class Game:

    def __init__(self):
        self.player_ids = []
        self.turn_order = []
        self.hands = []

    # @property
    # def is_running(self):
    #     # No hands, not running (game not started).
    #     # Have hands, but last hand is completed, then also not running (game finished)
    #     return bool(self.hands) and not self.current_hand.is_completed

    @property
    def current_hand(self):
        try:
            return self.hands[-1]
        except IndexError:
            raise exceptions.NotBegunError()

    def join(self):
        new_id = uuid.uuid4()
        self.player_ids.append(new_id)
        return new_id

    def begin(self):
        if len(self.player_ids) < 2:
            raise exceptions.InsufficientPlayersError()
        self.turn_order = self.player_ids.copy()
        random.shuffle(self.turn_order)  # Shuffle is an in-place operation!
        self.new_hand()

    def new_hand(self):
        if self.hands and not self.current_hand.is_completed:
            raise exceptions.HandInProgressError()
        self.hands.append(hand.Hand(len(self.hands)+1, self.turn_order))
