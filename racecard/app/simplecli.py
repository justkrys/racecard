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


import sys
from collections import namedtuple

from racecard.client import localclient


client = localclient.LocalClient()
Move = namedtuple("Move", "action target")


def get_num_players():
    num_players = 0
    while not 2 <= num_players <= 4:
        try:
            num_players = int(input("\nHow Many Players? [2-4] ").strip())  # nosec
            if not 2 <= num_players <= 4:
                raise ValueError
        except ValueError:
            print("Invalid choice, try again.")
    return num_players


def get_player_names(num_players):
    names = []
    for i in range(num_players):
        name = input(f"\nEnter Name for Player {i+1}: ").strip()  # nosec
        names.append(name)
    return names


def print_card_list(prefix, cards):
    print(
        prefix, ", ".join([f"{index+1}:[{card}]" for index, card in enumerate(cards)])
    )


def print_player_state(state):
    print_card_list("Hand:", state.hand)
    print_card_list("Safeties:", state.safeties)
    print_card_list("Coups Fourrés:", state.coups_fourres)
    print_card_list("Battle:", state.battle_pile)
    print_card_list("Speed:", state.speed_pile)
    print_card_list("Distance:", state.distance_pile)
    print("Total:", sum(card.value for card in state.distance_pile))


def print_player_states():
    for index, player in enumerate(client.players.values()):
        print(f"\nPlayer: {index+1}:[{player.name}]")
        state = client.get_player_state(player.id)
        print_player_state(state)


def print_move_help():
    print(
        """
Move Options:
    "H" for this help
    "D" to draw
    "X" to draw from the discard pile
    "D#" for discard card
    "#" (card) to play a card on yourself
    "##" (card then target player) to play on another player
    "Q" to quit

e.g. "D", "X", "D2", "6", "31", etc.
"""
    )


def is_valid_move(move):
    # Note: User input in 1-based not 0-based.
    hand_len = len(client.get_player_state().hand)
    # Single character inputs
    if move.target is None:
        if move.action in "dqx":
            # Valid single letter move
            return True
        if move.action.isdigit() and (0 < int(move.action) <= hand_len):
            # Valid play on yourself or valid hazard play in 2-player games
            return True
    # 2-character inputs
    if (
        move.action == "d"
        and move.target.isdigit()
        and (0 < int(move.target) <= hand_len)
    ):
        # Valid discard
        return True
    if (
        move.action.isdigit()
        and move.target.isdigit()
        and (0 < int(move.action) <= hand_len)
        and (0 < int(move.target) <= len(client.players))
    ):
        # Valid play on target
        return True
    return False


def get_player_move():
    print("\nYour turn: ", client.current_player.name)
    while True:
        move_str = (
            input("Choose move [D, X, D#, #, ##, Q, or H for help]: ")  # nosec
            .strip()
            .lower()
        )
        if move_str in ("h", "help"):
            print_move_help()
            continue
        move_len = len(move_str)
        if 0 < move_len < 3:  # Validate length
            # Normalize input
            move = Move._make((move_str, None) if move_len == 1 else tuple(move_str))
            if is_valid_move(move):
                break
        print("Invalid move, try again.")
    return move


def ask_yn(question):
    answer = None
    while answer not in ("y", "n"):
        answer = input(f"{question} [Y/N] ").strip().lower()  # nosec
    return answer == "y"


def handle_coup_fourre(player_id, safety_index):
    print(f"\nATTENTION {client.players[player_id].name}!")
    state = client.get_player_state(player_id)
    print_player_state(state)
    answer = ask_yn("Would you like to Coup Fourré?")
    if not answer:
        return
    client.coup_fourre(safety_index, player_id)


def handle_extension():
    if not client.is_hand_completed:
        raise RuntimeError("handle_extension called but hand is not done.")
    if not client.is_small_deck or client.is_hand_extended:
        return
    print(f"\nATTENTION {client.current_player.name}!")
    print_player_states()
    answer = ask_yn("Would you like to call an Extension?")
    if not answer:
        return
    client.extension()


def get_last_discarded():
    try:
        return str(client.top_discarded_card)
    except localclient.LocalClientError as error:
        return str(error)


def handle_play_result(result, target_id):
    if result is True:
        # Playing a distance card can return True if the player wins.
        handle_extension()
    elif result is False:
        # Hand is done, ran out of cards.
        pass  # Nothing to do, hand is done.
    elif isinstance(result, int):
        # Playing a hazard card can return the index of the target's
        # safety card that can Coup Fourré.
        if target_id is None and len(client.players) == 2:
            # In 2 a player game, targed_id can be omitted for
            # convenience.  Here we actaully need it.
            target_id = [id for id in client.players if id != client.current_player.id][
                0
            ]
        handle_coup_fourre(target_id, result)
    else:
        raise ValueError("Unknown play return value: " + repr(result))


def play_round():
    # Note: User input in 1-based not 0-based.
    current_round = client.round_number
    print("\nRound:", current_round)
    print("-" * 10)
    while client.round_number == current_round and not client.is_hand_completed:
        print("\nCards Remaining:", client.cards_remaining)
        print("Last Discarded:", get_last_discarded())
        print_player_states()
        move = get_player_move()
        if move.action == "q":
            sys.exit(0)
        try:
            if move.action == "d" and move.target is None:
                client.draw()
            elif move.action == "x" and move.target is None:
                client.draw_from_discard()
            elif move.action == "d":
                card_index = int(move.target) - 1
                client.discard(card_index)
            else:  # move.action is the index of a card to play
                card_index = int(move.action) - 1
                try:
                    target_index = int(move.target) - 1
                    target_id = client.players.values()[target_index].id
                except TypeError:
                    target_id = None
                result = client.play(card_index, target_id)
                if result is not None:
                    handle_play_result(result)
        except localclient.LocalClientError as error:
            print("\n" + str(error))


def play_hand():
    print("\nHand: ", client.hand_number)
    print("=" * 10)
    while not client.is_hand_completed:
        play_round()


def main():
    print(
        """
Race Card Copyright (C) 2020 Krys Lawrence
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain
conditions.  See the LICENCE file for details.

    """
    )
    print("Race Card!  Lets Race!")
    num_players = get_num_players()
    names = get_player_names(num_players)
    for name in names:
        client.add_player(name)
    print("\nBegin!")
    client.start_game()
    play_hand()


if __name__ == "__main__":
    main()
