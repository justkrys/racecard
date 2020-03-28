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


from racecard.core import deck


class PlayerState:

    def __init__(self):
        self.hand = []
        self.safeties = []  # All safeties, including the coup fourré cards.
        self.coups_fourres = []  # The safeties that were also coups fourrés.
        self.battle_pile = []
        self.speed_pile = []
        self.distance_pile = []

    @property
    def has_drawn(self):
        return len(self.hand) == 7

    @property
    def all_safeties(self):
        return self.safeties + self.coups_fourres

    @property
    def total(self):
        return sum(card.value for card in self.distance_pile)

    @property
    def is_rolling(self):
        if self.battle_pile and self.battle_pile[-1].type is deck.RemedyTypes.ROLL:
            return True
        if any([card.type is deck.SafetyTypes.RIGHT_OF_WAY for card in self.all_safeties]):
            return True
        return False
