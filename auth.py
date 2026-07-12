import requests

FIREBASE_API_KEY = "AIzaSyBhV6n0YKrFohrXsxT11Gwg-vCoRiEseaI"

def sign_up(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload, timeout=10)
    data = r.json()
    if "error" in data:
        return False, data["error"]["message"]
    return True, data

def sign_in(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload, timeout=10)
    data = r.json()
    if "error" in data:
        return False, data["error"]["message"]
    return True, data