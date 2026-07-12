import random
from utils import load_room, save_room

ROLES = ["Badshah", "Wazeer", "Sipahi", "Chor"]

def assign_roles(room_code):
    """4 players ko randomly 4 roles assign karta hai"""
    room = load_room(room_code)

    players = room["players"]
    shuffled_roles = ROLES.copy()
    random.shuffle(shuffled_roles)

    roles = {}
    for player, role in zip(players, shuffled_roles):
        roles[player] = role

    room["roles"] = roles
    room["game_started"] = True
    room["phase"] = "role_reveal"
    room["scores_calculated"] = False

    save_room(room_code, room)

def get_player_role(room_code, player_name):
    """Kisi specific player ka role return karta hai"""
    room = load_room(room_code)
    return room["roles"].get(player_name, None)

def check_and_start_game(room_code):
    """Check karta hai 4 players ho gaye to game start kar deta hai"""
    room = load_room(room_code)

    if len(room["players"]) == 4 and not room["game_started"]:
        assign_roles(room_code)
        return True
    return False

def get_reveal_info(room_code):
    """Badshah aur Wazeer ke naam return karta hai (public reveal ke liye)"""
    room = load_room(room_code)
    roles = room["roles"]

    badshah_name = None
    wazeer_name = None

    for player, role in roles.items():
        if role == "Badshah":
            badshah_name = player
        elif role == "Wazeer":
            wazeer_name = player

    return badshah_name, wazeer_name

def get_hidden_players(room_code):
    """Sipahi aur Chor (jo abhi reveal nahi huay) ke naam return karta hai"""
    room = load_room(room_code)
    roles = room["roles"]

    hidden = []
    for player, role in roles.items():
        if role in ["Sipahi", "Chor"]:
            hidden.append(player)

    return hidden

def submit_guess(room_code, guessed_player):
    """Wazeer ka guess save karta hai"""
    room = load_room(room_code)

    room["wazeer_guess"] = guessed_player
    room["phase"] = "result"

    save_room(room_code, room)

def is_guess_correct(room_code):
    """Check karta hai Wazeer ka guess sahi tha ya nahi"""
    room = load_room(room_code)

    actual_chor = None
    for player, role in room["roles"].items():
        if role == "Chor":
            actual_chor = player

    return room.get("wazeer_guess") == actual_chor

def start_next_round(room_code):
    """Naya round shuru karta hai - roles reshuffle karta hai"""
    room = load_room(room_code)

    room["current_round"] += 1

    if room["current_round"] > room["total_rounds"]:
        room["phase"] = "game_over"
    else:
        players = room["players"]
        shuffled_roles = ROLES.copy()
        random.shuffle(shuffled_roles)

        roles = {}
        for player, role in zip(players, shuffled_roles):
            roles[player] = role

        room["roles"] = roles
        room["phase"] = "role_reveal"
        room["scores_calculated"] = False
        room["wazeer_guess"] = None

    save_room(room_code, room)

def get_winner(room_code):
    """Sabse zyada score wale player(s) ka naam return karta hai"""
    room = load_room(room_code)
    scores = room["scores"]

    max_score = max(scores.values())
    winners = [player for player, score in scores.items() if score == max_score]

    return winners, max_score