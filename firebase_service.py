import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json

@st.cache_resource
def _init_firebase():
    if not firebase_admin._apps:
        if "firebase" in st.secrets:
            # Deployed environment (Streamlit Cloud) - secrets se credentials
            cred_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(cred_dict)
        else:
            # Local environment - JSON file se
            cred = credentials.Certificate("firebase-service-account.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = _init_firebase()


def load_data():
    """Saare rooms Firestore se fetch karke dict banata hai: {room_code: room_dict}
    NOTE: Yeh sirf tab use karo jab sach mein SAARI rooms chahiye ho (jaise Admin Panel).
    Ek room ke liye load_room() use karo — woh bohot zyada efficient hai."""
    docs = db.collection("rooms").stream()
    return {doc.id: doc.to_dict() for doc in docs}

def save_data(data):
    """Poora rooms dict Firestore mein likhta hai (har room = ek document)
    NOTE: Sirf tab use karo jab ek saath multiple rooms update karne hon.
    Ek room ke liye save_room() use karo."""
    for room_code, room_data in data.items():
        db.collection("rooms").document(room_code).set(room_data)

def save_room(room_code, room_data):
    """Ek hi room update karna ho to yeh save_data se zyada efficient hai"""
    db.collection("rooms").document(room_code).set(room_data)

def load_room(room_code):
    """Sirf EK room ka document fetch karta hai — poori collection nahi.
    Yeh sabse zyada use hoga (get_room, guess check, scoring, etc.)"""
    doc = db.collection("rooms").document(room_code).get()
    if doc.exists:
        return doc.to_dict()
    return None

def room_exists(room_code):
    """Sirf yeh check karta hai ki room code already liya gaya hai ya nahi —
    poori collection load kiye bina."""
    return db.collection("rooms").document(room_code).get().exists