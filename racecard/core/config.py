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


"""Core configuration and constants."""


TOTAL_SAFETIES = 4
NUM_SHUFFLES = 3
MAX_CARDS_IN_HAND = 6 + 1  # Hold 6, Draw 1
LARGE_DECK_PLAYERS = 4
MAX_PLAYERS = 6
SPEED_LIMIT_LIMIT = 50

SMALL_WIN_SCORE = 700
LARGE_WIN_SCORE = 1000
GAME_WIN_SCORE = 5000

SAFETY_SCORE = 100
ALL_SAFETIES_SCORE = 300
COUP_FOURRE_SCORE = 300
TRIP_COMPLETED_SCORE = 400
DELAYED_ACTION_SCORE = 300
SAFE_TRIP_SCORE = 300
SHUT_OUT_SCORE = 500
EXTENSION_SCORE = 200

D25_WEIGHT = 10
D50_WEIGHT = 11
D75_WEIGHT = 12
D100_WEIGHT = 13
D200_WEIGHT = 14

END_OF_LIMIT_WEIGHT = 20
SPARE_TIRE_WEIGHT = 21
REPAIRS_WEIGHT = 22
GASOLINE_WEIGHT = 23
ROLL_WEIGHT = 24

SPEED_LIMIT_WEIGHT = 30
STOP_WEIGHT = 31
OUT_OF_GASS_WEIGHT = 32
FLAT_TIRE_WEIGHT = 33
ACCIDENT_WEIGHT = 34

DRIVING_ACE_WEIGHT = 40
EXTRA_TANK_WEIGHT = 41
PUNCTURE_PROOF_WEIGHT = 42
RIGHT_OF_WAY_WEIGHT = 43
