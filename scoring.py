from utils import load_room, save_room

def calculate_scores(room_code, guess_correct):
    """Har player ka score update karta hai based on guess sahi tha ya nahi"""
    room = load_room(room_code)

    roles = room["roles"]

    for player, role in roles.items():
        points = 0

        if role == "Badshah":
            points = 100
        elif role == "Wazeer":
            points = 80 if guess_correct else -20
        elif role == "Sipahi":
            points = 50
        elif role == "Chor":
            points = 0 if guess_correct else 120

        room["scores"][player] = room["scores"].get(player, 0) + points

    save_room(room_code, room)

def get_scores(room_code):
    """Room ke saare players ka current score return karta hai"""
    room = load_room(room_code)
    return room["scores"]