import random
import string
from utils import load_room, save_room, room_exists

def generate_room_code():
    """6 letter/number ka unique room code banata hai"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_room(host_name, room_name="Untitled Room"):
    """Naya room banata hai aur host ko usme add karta hai"""
    room_code = generate_room_code()
    # agar galti se same code pehle se ho to naya banao
    while room_exists(room_code):
        room_code = generate_room_code()

    room_data = {
        "room_name": room_name,
        "players": [host_name],
        "roles": {},
        "scores": {host_name: 0},
        "current_round": 1,
        "total_rounds": 5,
        "game_started": False
    }

    save_room(room_code, room_data)
    return room_code

def join_room(room_code, player_name):
    """Player ko existing room mein add karta hai"""
    room = load_room(room_code)

    if room is None:
        return False, "Room code sahi nahi hai!"

    if len(room["players"]) >= 4:
        return False, "Room full hai! Sirf 4 players allowed hain."

    if player_name in room["players"]:
        return False, "Yeh naam already liya gaya hai is room mein."

    room["players"].append(player_name)
    room["scores"][player_name] = 0

    save_room(room_code, room)
    return True, "Room join ho gaya!"

def get_room(room_code):
    """Room ka current data return karta hai"""
    return load_room(room_code)

def leave_room(room_code, player_name):
    """Player ko room se nikalta hai"""
    room = load_room(room_code)
    if room is None:
        return False, "Room mojood nahi hai!"
    if player_name in room["players"]:
        room["players"].remove(player_name)
    if player_name in room.get("scores", {}):
        del room["scores"][player_name]
    save_room(room_code, room)
    return True, "Room chhod diya!"