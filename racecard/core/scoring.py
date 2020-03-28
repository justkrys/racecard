from racecard.core import deck


class ScoreCard:

    def __init__(self, player_id):
        self.player_id = player_id
        self.distance = 0
        self.safeties = 0
        self.all_safeties = 0
        self.coups_fourres = 0
        self.trip_completed = 0
        self.delayed_action = 0
        self.safe_trip = 0
        self.shut_out = 0
        self.extension = 0

    @property
    def total(self):
        return sum((
            self.distance,
            self.safeties,
            self.all_safeties,
            self.coups_fourres,
            self.trip_completed,
            self.delayed_action,
            self.safe_trip,
            self.shut_out,
            self.extension,
        ))


def score_player(player_id, hand):
    card = ScoreCard(player_id)
    player_state = hand.player_states[player_id]
    card.distance = player_state.total
    card.safeties = 100 * len(player_state.safeties)
    if len(player_state.safeties) == deck.TOTAL_SAFETIES:
        card.all_safeties = 300
    card.coups_fourres = 300 * len(player_state.coups_fourres)
    if (
            (card.distance == hand.SMALL_WIN_TARGET and hand.is_small_deck and not hand.is_extended)
            or (card.distance == hand.LARGE_WIN_TARGET and (hand.is_extended or not hand.is_small_deck))
    ):
        card.trip_completed = 400
    if card.trip_completed > 0:
        if hand.tray.is_draw_pile_empty():
            card.delayed_action = 300
        if not any([card.value == 200 for card in player_state.distance_pile]):
            card.safe_trip = 300
        if not any(bool(hand.get_player_state(id_).disance_pile) for id_ in hand.player_ids if id_ != player_id):
            card.shut_out = 500
        if hand.is_extended:
            card.extension = 200
    return card
