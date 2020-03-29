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

"""Responsible for calculating player scores."""

from racecard.core import deck


class ScoreCard(dict):
    """A player's score card, calculated after a hand is completed."""

    def __init__(self, player_id):
        super().__init__(
            {
                point_type: 0
                for point_type in (
                    "distance",
                    "safeties",
                    "all_safeties",
                    "coups_fourres",
                    "trip_completed",
                    "delayed_action",
                    "safe_trip",
                    "shut_out",
                    "extension",
                    "total",
                )
            }
        )
        self.player_id = player_id


def score_player(player_id, hand):
    """Create a ScoreCard for a player for the given completed hand and return it.

    Calculates the score based on the given hand.
    """
    card = ScoreCard(player_id)
    player_state = hand.get_player_state(player_id)
    card["distance"] = player_state.total
    card["safeties"] = 100 * len(player_state.safeties)
    if len(player_state.safeties) == deck.TOTAL_SAFETIES:
        card["all_safeties"] = 300
    card["coups_fourres"] = 300 * len(player_state.coups_fourres)
    if (
        card["distance"] == hand.SMALL_WIN_TARGET
        and hand.is_small_deck
        and not hand.is_extended
    ) or (
        card["distance"] == hand.LARGE_WIN_TARGET
        and (hand.is_extended or not hand.is_small_deck)
    ):
        card["trip_completed"] = 400
    if card["trip_completed"] > 0:
        if hand.is_draw_pile_empty:
            card["delayed_action"] = 300
        if not any([card.value == 200 for card in player_state.distance_pile]):
            card["safe_trip"] = 300
        if hand.is_shutout:
            card["shut_out"] = 500
        if hand.is_extended:
            card["extension"] = 200
    card["total"] = sum(card.values())
    return card
