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


"""Code to run/handle one hand of Race Card.  This is the heart of the game."""


from . import common, config, deck, exceptions, player, tray

PlayResults = common.Enum(  # pylint: disable=invalid-name
    "PlayResults",
    "OK CAN_COUP_FOURRE WIN_CAN_EXTEND WIN_CANNOT_EXTEND COMPLETED_NO_WINNER",
)


class Hand:
    """Represents and runs one hand of the game, consisting of several rounds."""

    def __init__(self, player_ids_in_turn_order):
        self.round_number = 1
        self.winner_id = None
        self.is_completed = False
        self._turn_index = 0
        self._extended = False
        self._last_target = None
        self._players = {
            player_id: player.Player() for player_id in player_ids_in_turn_order
        }
        self._small_deck = len(self._players) < config.LARGE_DECK_PLAYERS
        self._tray = tray.Tray(deck.make_deck(self._small_deck))
        self._win_score = (
            config.SMALL_WIN_SCORE if self._small_deck else config.LARGE_WIN_SCORE
        )
        self._deal_cards()

    # Internal Attributes

    @property
    def _can_extend(self):
        return self._small_deck and not self._extended

    @property
    def _no_more_cards(self):
        """Returns True if the draw pile and all player hands are empty.

        ... Or if the hand is already completed.
        """
        return (
            not self.is_completed
            and all([player.is_hand_empty for player in self._players.values()])
            and not self._tray.cards_remaining
        )

    def _deal_cards(self):
        self._ensure_not_completed()
        for _ in range(config.MAX_CARDS_IN_HAND - 1):
            for id_ in self._players:
                self._players[id_].recieve_card(self._tray.draw())

    def _ensure_completed(self):
        if not self.is_completed:
            raise exceptions.HandInProgressError()

    def _ensure_not_completed(self):
        if self.is_completed:
            raise exceptions.HandCompletedError()

    def _ensure_player_turn(self, player_id):
        if not player_id == self.current_player_id:
            raise exceptions.OutOfTurnError()

    def _ensure_hand_full(self, player_):
        """Checks that the player's hand is full or there are no more cards to draw."""
        if not player_.is_hand_full and self.cards_remaining > 0:
            raise exceptions.MustDrawError()

    def _ensure_can_draw(self, player_):
        """Checks that the player can draw a card unless there are no more to draw."""
        if player_.is_hand_full or not self.cards_remaining:
            raise exceptions.CannotDrawError()

    def _get_player(self, player_id):
        """Validates the given player id and returns the corresponding player."""
        if player_id not in self._players:
            raise exceptions.InvalidPlayerError()
        return self._players[player_id]

    def _resolve_target(self, player_id, target_id, card_type):
        """Returns the targed player or None if not applicable."""
        if card_type is deck.HazardCard:
            if target_id is None and len(self._players) == 2:
                target_id = [id_ for id_ in self._players if id_ != player_id][0]
            if target_id not in self._players:
                raise exceptions.InvalidTargetError()
            return self._players[target_id]
        return None

    def _next_turn(self):
        """Advances to the next turn and increments the round if necessary."""
        turn_index = self._turn_index
        turn_index += 1
        if turn_index >= len(self._players):
            self.round_number += 1
            turn_index = 0
        self._turn_index = turn_index

    @staticmethod
    def _play_safetycard(player_, card_index, _):
        """Handler for playing Safety cards."""
        player_.play_safety(card_index)
        return PlayResults.OK

    @staticmethod
    def _play_remedycard(player_, card_index, _):
        """Handler for playing Remedy cards."""
        player_.play_remedy(card_index)
        return PlayResults.OK

    def _play_hazardcard(self, player_, card_index, target):
        """Handler for playing Hazard cards."""
        card = player_.play_hazard(card_index)
        try:
            target.recieve_hazard(card)
        except exceptions.InvalidPlayError:
            player_.recieve_card(card)
            raise
        if target.can_coup_fourre:
            self._last_target = target
            return PlayResults.CAN_COUP_FOURRE
        return PlayResults.OK

    def _play_distancecard(self, player_, card_index, _):
        """Handler for playing Distance cards."""
        is_winner = player_.play_distance(card_index, self._win_score)
        if not is_winner:
            return PlayResults.OK
        if is_winner and self._can_extend:
            return PlayResults.WIN_CAN_EXTEND
        self._complete()
        return PlayResults.WIN_CANNOT_EXTEND

    def _complete(self, winner=True):
        """Complete the hand.  It is over."""
        self.winner_id = self.current_player_id if winner else None
        losers = [
            player for id_, player in self._players.items() if id_ != self.winner_id
        ]
        for loser in losers:
            loser.lost()
        shutout = all([loser.is_shutout for loser in losers])
        draw_empty = not self._tray.cards_remaining
        for player_ in self._players.values():
            player_.calc_score(draw_empty, self._extended, shutout)
        self.is_completed = True

    def _check_no_more_cards(self, result=None, next_turn=True):
        """Returns COMPLETE_NO_WINNER if there are no more cards to play.

        If there are still cards to play, returns result as a pass-through.
        """
        if self._no_more_cards:
            self._complete(winner=False)
            return PlayResults.COMPLETED_NO_WINNER
        if next_turn:
            self._next_turn()
        return result

    # Public Attributes

    @property
    def current_player_id(self):
        """Returns the id of the current player."""
        return tuple(self._players)[self._turn_index]

    @property
    def cards_remaining(self):
        """Returns the number of cards left in the deck."""
        return self._tray.cards_remaining

    @property
    def top_discarded_card(self):
        """Returns the top card on the discarded pile.

        Note: It does not remove the card from the pile. It just peeks at it.
        """
        return self._tray.top_discarded_card

    def get_player_state(self, player_id):
        """Returns the state of the given player."""
        return self._get_player(player_id).get_state()

    def draw(self, player_id, discard=False):
        """Draw a card from either the draw or discard pile."""
        self._ensure_not_completed()
        player_ = self._get_player(player_id)
        self._ensure_player_turn(player_id)
        self._ensure_can_draw(player_)
        player_.recieve_card(self._tray.draw(discard))

    def discard(self, player_id, card_index, force=False):
        """Discards a card from the player's hand.

        Attempting to discard a Safety will raise DiscardSafetyWarning unless force is
        set to True.
        """
        self._ensure_not_completed()
        player_ = self._get_player(player_id)
        self._ensure_player_turn(player_id)
        self._ensure_hand_full(player_)
        card = player_.discard(card_index, force)
        self._tray.discard(card)
        return self._check_no_more_cards()

    def play(self, player_id, card_index, target_id=None):
        """Dispatches a card play to the appropriate handler and returns any result.

        target_id is only used for hazards.
        If target_id is None, and this is a 2-player game, then the other player is
        automatically selected as the target.
        """
        self._ensure_not_completed()
        player_ = self._get_player(player_id)
        self._ensure_player_turn(player_id)
        self._ensure_hand_full(player_)
        card_type = player_.card_type(card_index)
        target = self._resolve_target(player_id, target_id, card_type)
        self._last_target = None
        handler_name = "_play_" + card_type.__name__.lower()
        result = getattr(self, handler_name)(player_, card_index, target)
        # No exceptions raised so far so play was successful.
        next_turn = (
            card_type is not deck.SafetyCard and result != PlayResults.WIN_CAN_EXTEND
        )
        return self._check_no_more_cards(result, next_turn=next_turn)

    def coup_fourre(self, player_id):
        """Triggers a Coup Fourré if possible."""
        self._ensure_not_completed()
        player_ = self._get_player(player_id)
        # Even if multiple players think they can Coup Fourré, only the player that last
        # recieved a hazard card is allowed to Coup Fourré.
        if player_ != self._last_target:
            raise exceptions.CannotCoupFourreError()
        discards = player_.coup_fourre()
        # No exception raised, so the coup was successful.
        for card in discards:
            self._tray.discard(card)
        self._last_target = None
        self._turn_index = tuple(self._players).index(player_id)

    def extension(self, player_id):
        """Call an extension to the game."""
        self._ensure_not_completed()
        player_ = self._get_player(player_id)
        self._ensure_player_turn(player_id)
        if not self._can_extend or not player_.is_winner:
            raise exceptions.CannotExtendError()
        player_.extension()
        self._win_score = config.LARGE_WIN_SCORE
        self._extended = True
        self._next_turn()

    def no_extension(self, player_id):
        """Signal that an extension was declined and the hand should complete."""
        self._ensure_not_completed()
        player_ = self._get_player(player_id)
        self._ensure_player_turn(player_id)
        if not self._can_extend or not player_.is_winner:
            raise exceptions.CannotExtendError()
        self._complete()

    def toggle_sort(self, player_id):
        """Toggles whether or not a player's hand should always be sorted."""
        self._ensure_not_completed()
        player_ = self._get_player(player_id)
        player_.toggle_sort()
