from firebase_service import load_data, save_data, load_room, save_room, room_exists  # Ab Firestore backend use hota hai (purana JSON file tareeqa hata diya)
def get_role_style(role):
    """Har role ke liye emoji aur color return karta hai"""
    styles = {
        "Badshah": {"emoji": "👑", "color": "#FFD700", "bg": "#4a3c00"},
        "Wazeer": {"emoji": "🧠", "color": "#FF69B4", "bg": "#4a1f35"},
        "Sipahi": {"emoji": "⚔️", "color": "#00BFFF", "bg": "#0d3a4a"},
        "Chor": {"emoji": "🥷", "color": "#FF4500", "bg": "#4a1500"},
    }
    return styles.get(role, {"emoji": "❓", "color": "#FFFFFF", "bg": "#333333"})

AVATAR_LIST = ["🦁", "🐯", "🦅", "🐺", "🦊", "🐻", "🐼", "🦉"]

def get_avatar(player_name):
    """Player ke naam se hamesha same avatar generate karta hai"""
    index = sum(ord(char) for char in player_name) % len(AVATAR_LIST)
    return AVATAR_LIST[index]

def get_role_style(role):
    """Har role ke liye emoji aur color return karta hai"""
    styles = {
        "Badshah": {"emoji": "👑", "color": "#FFD700", "bg": "#4a3c00"},
        "Wazeer": {"emoji": "🧠", "color": "#FF69B4", "bg": "#4a1f35"},
        "Sipahi": {"emoji": "⚔️", "color": "#00BFFF", "bg": "#0d3a4a"},
        "Chor": {"emoji": "🥷", "color": "#FF4500", "bg": "#4a1500"},
    }
    return styles.get(role, {"emoji": "❓", "color": "#FFFFFF", "bg": "#333333"})

AVATAR_LIST = ["🦁", "🐯", "🦅", "🐺", "🦊", "🐻", "🐼", "🦉"]

def get_avatar(player_name):
    """Player ke naam se hamesha same avatar generate karta hai"""
    index = sum(ord(char) for char in player_name) % len(AVATAR_LIST)
    return AVATAR_LIST[index]