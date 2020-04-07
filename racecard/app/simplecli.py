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


"""A simple CLI interface to Race Card."""


import sys
from dataclasses import asdict, dataclass

from racecard.core import exceptions
from racecard.core.game import Game, PlayResults


class QuitException(exceptions.ExceptionBase):
    """Raised when quitting the game."""


@dataclass
class Move:
    """A player's move, as entered by the user."""

    action: str
    target: str = None


game = Game()  # pylint: disable=invalid-name
player_names = {}  # pylint: disable=invalid-name


def get_num_players():
    """Asks user how many players in the game and returns result."""
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
    """Asks user for the name of each player and returns results as a list."""
    names = []
    for i in range(num_players):
        name = input(f"\nEnter Name for Player {i+1}: ").strip()  # nosec
        names.append(name)
    return names


def print_card_list(prefix, cards):
    """Print the list of cards."""
    print(
        prefix, ", ".join([f"{index+1}:[{card}]" for index, card in enumerate(cards)])
    )


def print_player_state(state):
    """Print the state of a player."""
    print_card_list("Hand:", state.hand)
    print_card_list("Safeties:", state.safeties_pile)
    print_card_list("Battle:", state.battle_pile)
    print_card_list("Speed:", state.speed_pile)
    print_card_list("Distance:", state.distance_pile)
    print("Total:", state.total)


def print_player_states():
    """Print the state of all players."""
    for index, (id_, name) in enumerate(player_names.items()):
        print(f"\nPlayer: {index+1}:[{name}]")
        state = game.get_player_state(id_)
        print("State:", state.state)
        print("Coups Fourrés:", state.coups_fourres)
        print_player_state(state)


def print_move_help():
    """Print a help message for entering valid moves."""
    print(
        """
Move Options:
    "H" for this help
    "D" to draw
    "X" to draw from the discard pile
    "D#" for discard card
    "#" (card) to play a card on yourself
    "##" (card then target player) to play on another player
    "S" to toggle auto sorting of your hand
    "Q" to quit

e.g. "D", "X", "D2", "6", "31", etc.
"""
    )


def is_valid_move(move):
    """Returns True is the move is formatted correctly, False otherwise."""
    # Note: User input in 1-based not 0-based.
    hand_len = len(game.get_player_state(game.current_player_id).hand)
    # Single character inputs
    if move.target is None:
        if move.action in "dqsx":
            # Valid single letter move
            return True
        if move.action.isdigit() and (0 < int(move.action) <= hand_len):
            # Valid play on yourself or valid hazard play in 2-player games
            return True
        return False
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
        and (0 < int(move.target) <= len(player_names))
    ):
        # Valid play on target
        return True
    return False


def get_player_move(player_id):
    """Asks player for their next move and returns result."""
    print("\nYour turn: ", player_names[player_id])
    while True:
        move_str = (
            input("Choose move [D, X, D#, #, ##, S, Q, or H for help]: ")  # nosec
            .strip()
            .lower()
        )
        if move_str in ("h", "help"):
            print_move_help()
            continue
        move_len = len(move_str)
        if 0 < move_len < 3:  # Validate length
            # Normalize input
            move = Move(move_str) if move_len == 1 else Move(*move_str)
            if is_valid_move(move):
                break
        print("Invalid move, try again.")
    return move


def ask_yn(question):
    """Ask user a Yes or No questions and return response."""
    answer = None
    while answer not in ("y", "n"):
        answer = input(f"{question} [Y/N] ").strip().lower()  # nosec
    return answer == "y"


def handle_coup_fourre(target_id):
    """Handles Coup Fourré oppotunity by asking player and then triggering it.

    target_id is the player who was attacked and can coup fourré.
    """
    # Note: target_id can be different from the current player when there are more than
    # 2 players.  Also, the attacking player's turn has already ended at this point and
    # the current player is the next one in turn order.
    if target_id is None and len(player_names) == 2:
        # In 2 a player game, target_id can be omitted for convenience (==None).  Here
        # we actually need it.  But in this case we know it is the current player since
        # there are only 2 players.
        target_id = game.current_player_id
    state = game.get_player_state(target_id)
    print_player_state(state)
    print(f"\nATTENTION {player_names[target_id]}!")
    if ask_yn("Would you like to Coup Fourré?"):
        game.coup_fourre(target_id)


def handle_extension(player_id):
    """Handles end of round extension opportunity by asking player and triggering it."""
    print(f"\nATTENTION {player_names[player_id]}!")
    if ask_yn("Would you like to call an Extension?"):
        game.extension(player_id)
    else:
        game.no_extension(player_id)


def get_last_discarded():
    """Returns the last card that was discarded."""
    try:
        return str(game.top_discarded_card)
    except exceptions.EmptyPileError as error:
        return str(error)


def handle_play_result(result, player_id, target_id):
    """Handles the result of sending a play to ther server."""
    if result == PlayResults.WIN_CAN_EXTEND:
        # Playing a distance card can return True if the player wins.
        handle_extension(player_id)
    elif result == PlayResults.CAN_COUP_FOURRE:
        handle_coup_fourre(target_id)


def handle_discard(player_id, move):
    """Handles discarding a card, even if it is a Safety."""
    card_index = int(move.target) - 1
    try:
        game.discard(player_id, card_index)
    except exceptions.DiscardSafetyWarning:
        if ask_yn("WARNING: Are you sure you want to discard a Safety card?!"):
            game.discard(player_id, card_index, force=True)


def get_target_id(move):
    """Returns the player id of the target from move, or None if not possible."""
    try:
        target_index = int(move.target) - 1
        return tuple(player_names)[target_index]
    except TypeError:
        return None


def play_round():
    """Plays one round by presenting state, asking for input and sending the play."""
    # Note: User input in 1-based not 0-based.
    current_round = game.round_number
    print("\nRound:", current_round)
    print("-" * 10)
    while game.round_number == current_round and not game.is_hand_completed:
        print("\nCards Remaining:", game.cards_remaining)
        print("Last Discarded:", get_last_discarded())
        print_player_states()
        player_id = game.current_player_id
        move = get_player_move(player_id)
        if move.action == "q":
            raise QuitException()
        try:
            if move.action == "d" and move.target is None:
                game.draw(player_id)
            elif move.action == "x" and move.target is None:
                game.draw(player_id, discard=True)
            elif move.action == "s" and move.target is None:
                game.toggle_sort(player_id)
            elif move.action == "d":
                handle_discard(player_id, move)
            else:  # move.action is the index of a card to play
                card_index = int(move.action) - 1
                target_id = get_target_id(move)
                result = game.play(player_id, card_index, target_id)
                handle_play_result(result, player_id, target_id)
        except exceptions.CoreException as error:
            print("\nATTENTION:", str(error))
        print("-" * 10)


def print_scores(title_prefix, winner_id=None):
    """Print the scores of all players.

    A title with the given prefix is printed at the top of all the scores.
    """
    print("=" * 10)
    print(f"\n{title_prefix} SCORES:\n")
    for index, (id_, name) in enumerate(player_names.items()):
        winner = "WINNER!" if id_ == winner_id else ""
        print("-" * 10)
        print(f"Player {index+1}: [{name}] {winner}\n")
        score_card = asdict(game.get_player_state(id_).score_card)
        for point_type, score in score_card.items():
            point_type = point_type.replace("_", " ").title()
            print(f"{point_type}: {score}")
        print()
    print("=" * 10)


def play_hand():
    """Plays one hand by repeatedly playing rounds until hand is completed."""
    print("\nHand: ", game.hand_number)
    print("=" * 10)
    while not game.is_hand_completed:
        play_round()
    if game.hand_winner_id is not None:
        winner = player_names[game.hand_winner_id]
        print(f"\nHUZZAH! Winner: {winner}! Congratulations!")
    else:
        print("Awww. No winner this hand.")
    print_scores(f"HAND {game.hand_number}", game.hand_winner_id)


def main():
    """Main entry point for the simple ClI interface."""
    print(
        """
Race Card Copyright (C) 2020 Krys Lawrence
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain
conditions.  See the LICENCE file for details.

    """
    )
    print("Race Card!  Lets Race!")
    try:
        num_players = get_num_players()
        names = get_player_names(num_players)
        for name in names:
            id_ = game.add_player()
            player_names[id_] = name
        print("\nBegin!")
        game.begin()
        next_hand = True
        while next_hand:
            play_hand()
            next_hand = ask_yn("\nPlay next hand?")
            if next_hand:
                game.next_hand()
        print("\n Good Game!")
        print_scores("FINAL", game.winner_id)
        raise QuitException()
    except QuitException:
        print("See you!  See you in the mosh'sh pit!")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\nAww... Bye bye. :(")
        sys.exit(-1)


if __name__ == "__main__":
    main()
