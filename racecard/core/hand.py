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


from racecard.core import exceptions, playerstate, deck, tray, scoring


class Hand:

    MAX_CARDS_IN_HAND = 6
    SMALL_WIN_TARGET = 700
    LARGE_WIN_TARGET = 1000
    LARGE_DECK_PLAYERS = 4

    def __init__(self, number, player_ids_in_turn_order):
        self.number = number
        self.round = 1
        self.is_extended = False
        self.is_completed = False
        self._player_ids = player_ids_in_turn_order
        self._turn_index = 0
        self._last_target_id = None
        self._player_states = {}
        self._winner_id = None
        self._player_scores = {}
        self._win_target = (self.SMALL_WIN_TARGET if self.is_small_deck else self.LARGE_WIN_TARGET)
        self._tray = tray.Tray(deck.make_deck(self.is_small_deck))
        for player_id in self._player_ids:
            self._player_states[player_id] = playerstate.PlayerState()
        self._deal_cards()

    # Internal Methods

    def _deal_cards(self):
        self._check_not_completed()
        for _ in range(self.MAX_CARDS_IN_HAND):
            for id_ in self._player_ids:
                self._player_states[id_].hand.append(self._tray.draw())

    def _check_completed(self):
        if not self.is_completed:
            raise exceptions.HandInProgressError()

    def _check_not_completed(self):
        if self.is_completed:
            raise exceptions.HandCompletedError()

    def _check_player_id(self, player_id):
        if player_id is None:
            return self.current_player_id
        if player_id not in self._player_ids:
            raise exceptions.InvalidPlayerError()
        return player_id

    def _check_player_turn(self, player_id):
        if not player_id == self.current_player_id:
            raise exceptions.OutOfTurnError()

    def _check_has_drawn(self, player_state):
        if not player_state.has_drawn and self.cards_remaining > 0:
            raise exceptions.MustDrawError()

    @staticmethod
    def _get_card(state, card_index):
        try:
            return state.hand[card_index]
        except IndexError:
            raise exceptions.InvalidCardIndexError()

    def _no_coup_fourre(self):
        self._last_target_id = None

    def _play_hazard(self, card_index, card, player_state, target_id=None):
        if target_id is None:
            if len(self._player_ids) > 2:
                raise exceptions.AmbiguousTargetError()
            # Only 2 players, so we can infer that target_id is the other player.
            target_id = self._player_ids[self._turn_index-1]
        else:
            target_id = self._check_player_id(target_id)  # Validate the id
        if target_id == self.current_player_id:
            raise exceptions.InvalidPlayError()
        target_state = self._player_states[target_id]
        if any(card.prevented_by is safety.type for safety in target_state.all_safeties):
            raise exceptions.InvalidPlayError()
        pile = (target_state.battle_pile if card.pile is deck.CardPiles.BATTLE else target_state.speed_pile)
        pile.append(player_state.hand.pop(card_index))
        # Check for possible Coup Fourré.  Return the safety card's index if one is possible.
        for index, target_card in enumerate(target_state.hand):
            if target_card.kind is deck.CardKinds.SAFETY and card.type in target_card.prevents:
                self._last_target_id = target_id
                return index

    def _play_distance(self, card_index, card, state):
        if not state.is_rolling:
            raise exceptions.InvalidPlayError()
        if state.speed_pile and card.prevented_by is state.speed_pile[-1].type:
            raise exceptions.InvalidPlayError()
        d200_count = sum(1 for card in state.distance_pile if card.type is deck.DistanceTypes.D200)
        if card.type is deck.DistanceTypes.D200 and d200_count >= 2:
            raise exceptions.InvalidPlayError()
        total = card.value + state.total
        if total > self._win_target:
            raise exceptions.InvalidPlayError()
        state.distance_pile.append(state.hand.pop(card_index))
        if total == self._win_target:
            self.is_completed = True
            self._winner_id = self.current_player_id
            return True, False  # Win, no next turn.

    @staticmethod
    def _play_remedy(card_index, card, state):
        pile = (state.battle_pile if card.pile is deck.CardPiles.BATTLE else state.speed_pile)
        if (not pile and card.type is not deck.RemedyTypes.ROLL) or (pile and not pile[-1].type in card.applies_to):
            raise exceptions.InvalidPlayError()
        pile.append(state.hand.pop(card_index))

    def _play_safety(self, card_index, card, state):
        if state.battle_pile and state.battle_pile[-1].type in card.prevents:
            self._tray.discard(state.battle_pile.pop())
        if state.speed_pile and state.speed_pile[-1].type in card.prevents:
            self._tray.discard(state.speed_pile.pop())
        state.safeties.append(state.hand.pop(card_index))
        return None, False  # Play again.

    def _next_player(self):
        self._turn_index += 1
        if self._turn_index >= len(self._player_ids):
            self._turn_index = 0
            self.round += 1

    def _is_all_hands_empty(self):
        return not any(bool(state.hand) for state in self._player_states.values())

    # Public Methods

    @property
    def cards_remaining(self):
        return self._tray.cards_remaining

    @property
    def top_discarded_card(self):
        return self._tray.top_discarded_card

    @property
    def current_player_id(self):
        return self._player_ids[self._turn_index]

    @property
    def is_small_deck(self):
        return len(self._player_ids) < self.LARGE_DECK_PLAYERS

    def get_player_state(self, player_id=None):
        player_id = self._check_player_id(player_id)
        return self._player_states[player_id]

    def draw(self, player_id=None):
        self._check_not_completed()
        player_id = self._check_player_id(player_id)
        self._check_player_turn(player_id)
        state = self._player_states[player_id]
        if state.has_drawn:
            raise exceptions.AlreadyDrawnError()
        self._no_coup_fourre()
        state.hand.append(self._tray.draw())

    def draw_from_discard(self, player_id=None):
        self._check_not_completed()
        player_id = self._check_player_id(player_id)
        self._check_player_turn(player_id)
        state = self._player_states[player_id]
        if state.has_drawn:
            raise exceptions.AlreadyDrawnError()
        self._no_coup_fourre()
        state.hand.append(self._tray.draw_from_discard())

    def play(self, card_index, target_id=None, player_id=None):
        self._check_not_completed()
        player_id = self._check_player_id(player_id)
        self._check_player_turn(player_id)
        state = self._player_states[self.current_player_id]
        self._check_has_drawn(state)
        card = self._get_card(state, card_index)
        if card.kind is deck.CardKinds.HAZARD:
            self._no_coup_fourre()
            safety_index = self._play_hazard(card_index, card, state, target_id)
            self._next_player()
            return safety_index
        if target_id is not None and target_id != self.current_player_id:
            raise exceptions.InvalidTargetError()
        self._no_coup_fourre()
        # All self-play methods have the same signature.
        # If _play_X method returns a value, it must be a tuple of (value-to-return-to-caller, go-to-next-player?)
        result = getattr(self, f'_play_{card.kind.name.lower()}')(card_index, card, state)
        if result is None:
            next_player = True
        else:
            result, next_player = result
        if self._is_all_hands_empty():
            self.is_completed = True
            self._winner_id = None
            return False
        if next_player:  # Any other return value should just be passed through.
            self._next_player()
        return result

    def discard(self, card_index, player_id=None):
        self._check_not_completed()
        player_id = self._check_player_id(player_id)
        self._check_player_turn(player_id)
        state = self._player_states[player_id]
        self._check_has_drawn(state)
        self._get_card(state, card_index)  # Validates card_index
        self._no_coup_fourre()
        self._tray.discard(state.hand.pop(card_index))
        self._next_player()

    def coup_fourre(self, safety_index, player_id=None):
        self._check_not_completed()
        player_id = self._check_player_id(player_id)
        if player_id != self._last_target_id:
            raise exceptions.InvalidPlayError()
        state = self._player_states[player_id]
        card = self._get_card(state, safety_index)
        valid_play = False
        for pile in (state.battle_pile, state.speed_pile):
            if not pile:
                continue
            top_card = pile[-1]
            if top_card.kind is deck.CardKinds.HAZARD and top_card.type in card.prevents:
                valid_play = True
                self._tray.discard(pile.pop())
        if not valid_play:
            raise exceptions.InvalidPlayError()
        self._no_coup_fourre()
        state.coups_fourres.append(state.hand.pop(safety_index))

    def extension(self, winner_id=None):
        player_id = self._check_player_id(winner_id)
        if self.is_extended:
            raise exceptions.AlreadyExtendedError()
        self._check_completed()
        if player_id != self._winner_id:
            raise exceptions.OutOfTurnError()
        if not self.is_small_deck:
            raise exceptions.ExtensionNotAllowedError()
        self.is_completed = False
        self.is_extended = True
        self._win_target = self.LARGE_WIN_TARGET
        self._next_player()

    def get_player_scores(self):
        self._check_completed()
        if not self._player_scores:
            for player_id in self._player_ids:
                self._player_scores[player_id] = scoring.score_player(player_id, self)
        return self._player_scores
