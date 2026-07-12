import streamlit as st
import streamlit.components.v1 as components
import os
import json
import base64
import time
from streamlit_autorefresh import st_autorefresh
from room import create_room, join_room, get_room
from game import (
    check_and_start_game, get_player_role, get_reveal_info,
    get_hidden_players, submit_guess, is_guess_correct,
    start_next_round, get_winner
)
from scoring import calculate_scores, get_scores
from utils import load_data, save_data, save_room, get_role_style, get_avatar
from auth import sign_up, sign_in
from config import ADMIN_EMAILS

st.set_page_config(page_title="Badshah Ka Wazeer Kon", page_icon="👑")

# ---------- PROFILE PICTURE STORAGE ----------
PROFILE_FILE = "data/profiles.json"

@st.cache_data(ttl=5)
def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        return {}
    try:
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_profile_picture(name, image_bytes):
    os.makedirs("data", exist_ok=True)
    profiles = load_profiles()
    profiles[name] = base64.b64encode(image_bytes).decode("utf-8")
    with open(PROFILE_FILE, "w") as f:
        json.dump(profiles, f)
    load_profiles.clear()

def get_avatar_html(name, size=30):
    profiles = load_profiles()
    if name in profiles:
        b64 = profiles[name]
        return (
            f'<img src="data:image/png;base64,{b64}" '
            f'style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;'
            f'vertical-align:middle;border:2px solid #FFD700;margin-right:6px;">'
        )
    return f'<span style="margin-right:4px;">{get_avatar(name)}</span>'

# ---------- ANIMATED ROYAL GAMING BACKGROUND ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700;900&family=Poppins:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background-color: #1a0a2e;
    background-image:
        radial-gradient(ellipse at top, #2d1b4e 0%, #1a0a2e 40%, #0a0515 100%),
        radial-gradient(2px 2px at 10% 20%, #FFD700, transparent),
        radial-gradient(2px 2px at 80% 10%, #ffffff, transparent),
        radial-gradient(1.5px 1.5px at 30% 50%, #FFD700, transparent),
        radial-gradient(2px 2px at 60% 70%, #ffffff, transparent),
        radial-gradient(1.5px 1.5px at 90% 40%, #FFD700, transparent),
        radial-gradient(2px 2px at 15% 85%, #ffffff, transparent),
        radial-gradient(1.5px 1.5px at 45% 15%, #FFD700, transparent),
        radial-gradient(2px 2px at 75% 90%, #ffffff, transparent),
        radial-gradient(circle, rgba(255,215,0,0.08) 0%, transparent 70%);
    background-repeat: no-repeat, repeat, repeat, repeat, repeat, repeat, repeat, repeat, repeat, no-repeat;
    background-size: 100% 100%, 300px 300px, 300px 300px, 300px 300px, 300px 300px, 300px 300px, 300px 300px, 300px 300px, 300px 300px, 60% 60%;
    background-position: center, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, -10% -20%;
    background-attachment: fixed;
}

.floating-orbs {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
}
.floating-orbs span {
    position: absolute;
    border-radius: 50%;
    filter: blur(30px);
    opacity: 0.35;
}
.floating-orbs span:nth-child(1) {
    width: 260px; height: 260px;
    top: 5%; left: 8%;
    background: radial-gradient(circle, #FFD700, transparent 70%);
    animation: floatA 14s ease-in-out infinite;
}
.floating-orbs span:nth-child(2) {
    width: 320px; height: 320px;
    top: 55%; right: 10%;
    background: radial-gradient(circle, #7b5fff, transparent 70%);
    animation: floatB 18s ease-in-out infinite;
}
.floating-orbs span:nth-child(3) {
    width: 180px; height: 180px;
    bottom: 8%; left: 35%;
    background: radial-gradient(circle, #ff6ec7, transparent 70%);
    animation: floatC 16s ease-in-out infinite;
}
@keyframes floatA {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(40px, 60px) scale(1.15); }
}
@keyframes floatB {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(-50px, -30px) scale(1.1); }
}
@keyframes floatC {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(30px, -40px) scale(1.2); }
}

h1 {
    text-align: center;
    font-family: 'Cinzel Decorative', serif;
    font-weight: 900;
    background: linear-gradient(90deg, #FFD700, #FFF8DC, #FFD700);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-size: 200% auto;
    animation: shimmer 3s linear infinite;
    text-shadow: 0 0 25px rgba(255, 215, 0, 0.4);
    padding-bottom: 10px;
}

.room-name-title {
    text-align: center;
    font-family: 'Cinzel Decorative', serif;
    font-weight: 900;
    font-size: 34px;
    background: linear-gradient(90deg, #FFD700, #FFF8DC, #FFD700);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-size: 200% auto;
    animation: shimmer 3s linear infinite;
    text-shadow: 0 0 20px rgba(255, 215, 0, 0.35);
    margin-bottom: 4px;
}

@keyframes shimmer {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}

h2, h3 {
    font-family: 'Cinzel Decorative', serif;
    color: #FFD700 !important;
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
}

div[data-testid="column"] {
    background: linear-gradient(160deg, rgba(255,215,0,0.06), rgba(123,95,255,0.05));
    border: 2px solid rgba(255, 215, 0, 0.55);
    border-radius: 18px;
    padding: 24px 22px;
    backdrop-filter: blur(12px);
    box-shadow:
        0 4px 25px rgba(0, 0, 0, 0.45),
        0 0 18px rgba(255, 215, 0, 0.25),
        inset 0 0 20px rgba(255, 215, 0, 0.04);
    transition: box-shadow 0.3s ease, transform 0.3s ease, border-color 0.3s ease;
    animation: cardPulse 3s ease-in-out infinite;
}
div[data-testid="column"]:hover {
    border-color: #FFD700;
    box-shadow:
        0 0 35px rgba(255, 215, 0, 0.55),
        0 0 60px rgba(255, 215, 0, 0.15),
        inset 0 0 25px rgba(255, 215, 0, 0.08);
    transform: translateY(-4px);
}
@keyframes cardPulse {
    0%, 100% {
        box-shadow:
            0 4px 25px rgba(0, 0, 0, 0.45),
            0 0 14px rgba(255, 215, 0, 0.2),
            inset 0 0 20px rgba(255, 215, 0, 0.04);
    }
    50% {
        box-shadow:
            0 4px 25px rgba(0, 0, 0, 0.45),
            0 0 26px rgba(255, 215, 0, 0.4),
            inset 0 0 20px rgba(255, 215, 0, 0.06);
    }
}

div[data-testid="stTextInput"] input {
    background: rgba(0, 0, 0, 0.45) !important;
    border: 1.5px solid rgba(255, 215, 0, 0.4) !important;
    border-radius: 10px !important;
    color: #FFF8DC !important;
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #FFD700 !important;
    box-shadow: 0 0 14px rgba(255, 215, 0, 0.5) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #3a1c66, #1a0a2e) !important;
    color: #FFD700 !important;
    font-weight: 600 !important;
    border: 2px solid #FFD700 !important;
    border-radius: 12px !important;
    padding: 8px 20px !important;
    transition: all 0.3s ease;
    animation: pulseGlow 2.5s ease-in-out infinite;
}
.stButton > button:hover {
    box-shadow: 0 0 22px rgba(255, 215, 0, 0.75) !important;
    transform: scale(1.05);
    color: #FFF8DC !important;
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 6px rgba(255, 215, 0, 0.25); }
    50% { box-shadow: 0 0 16px rgba(255, 215, 0, 0.45); }
}

div[data-testid="stAlert"] {
    border-radius: 14px !important;
    border: 1px solid rgba(255, 215, 0, 0.35) !important;
    backdrop-filter: blur(6px);
}

.profile-avatar-label {
    display: block;
    width: 100%;
    text-align: center;
    font-size: 15px;
    color: #FFD700;
    font-family: 'Poppins', sans-serif;
    margin-top: 4px;
    transform: translateX(-62px);
}

/* ---- Loading splash screen ---- */
.splash-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 70vh;
    gap: 18px;
}
.splash-crown {
    font-size: 80px;
    animation: splashSpin 1.4s ease-in-out infinite;
}
@keyframes splashSpin {
    0%, 100% { transform: scale(1) rotate(0deg); }
    50% { transform: scale(1.15) rotate(8deg); }
}
.splash-text {
    font-family: 'Cinzel Decorative', serif;
    font-size: 22px;
    color: #FFD700;
    text-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
}

/* ---- Login / Signup professional card ---- */
.login-header-wrap {
    text-align: center;
    margin-top: 6px;
    margin-bottom: 24px;
}
.login-crown {
    font-size: 46px;
    margin-bottom: 4px;
    filter: drop-shadow(0 0 12px rgba(255, 215, 0, 0.45));
}
.login-title {
    font-family: 'Cinzel Decorative', serif;
    font-size: 22px;
    color: #FFD700;
    text-shadow: 0 0 12px rgba(255, 215, 0, 0.4);
    margin-bottom: 4px;
}
.login-subtitle {
    font-family: 'Poppins', sans-serif;
    font-size: 13px;
    color: rgba(255, 248, 220, 0.55);
    letter-spacing: 0.6px;
}

div[data-testid="stTabs"] {
    max-width: 420px;
    margin: 0 auto;
}
div[data-testid="stTabs"] div[role="tablist"] {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 12px;
    border: 1.5px solid rgba(255, 215, 0, 0.3);
    padding: 5px;
    gap: 4px;
    justify-content: center;
}
div[data-testid="stTabs"] button[role="tab"] {
    flex: 1;
    border-radius: 9px !important;
    color: rgba(255, 248, 220, 0.65) !important;
    font-weight: 600;
    transition: all 0.25s ease;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #3a1c66, #1a0a2e) !important;
    color: #FFD700 !important;
    box-shadow: 0 0 12px rgba(255, 215, 0, 0.3);
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: #FFD700 !important;
}
div[data-testid="stTabs"] div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stTabs"] div[data-testid="stVerticalBlock"] {
    padding-top: 18px;
}
div[data-testid="stTabs"] .stButton > button {
    width: 100%;
    margin-top: 10px;
    letter-spacing: 0.5px;
}
div[data-testid="stTabs"] div[data-testid="stTextInput"] {
    margin-bottom: 4px;
}

.main .block-container,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section.main {
    position: relative;
    z-index: 1;
}

[data-testid="stAppViewContainer"] > * {
    position: relative;
    z-index: 1;
}

/* ---- Sidebar poori tarah hide karo (Admin portal sirf profile link se accessible) ---- */
[data-testid="stSidebar"] {
    display: none;
}
[data-testid="collapsedControl"] {
    display: none;
}

/* ---- Profile popover button: circle, chevron hide, perfect center, bara size ---- */
div[data-testid="stPopover"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    text-align: center !important;
}
div[data-testid="stPopover"] button {
    border-radius: 50% !important;
    width: 100px !important;
    height: 100px !important;
    min-width: 100px !important;
    max-width: 100px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: hidden !important;
    animation: none !important;
    box-shadow: 0 0 18px rgba(255, 215, 0, 0.45) !important;
    margin: 0 auto !important;
    background-position: center center !important;
    background-size: cover !important;
}
div[data-testid="stPopover"] button [data-testid="stIconMaterial"] {
    display: none !important;
}
div[data-testid="stPopover"] button svg {
    display: none !important;
}
</style>

<div class="floating-orbs">
    <span></span>
    <span></span>
    <span></span>
</div>
""", unsafe_allow_html=True)

# ---------- SESSION STATE INIT ----------
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "room_code" not in st.session_state:
    st.session_state.room_code = ""
if "joined" not in st.session_state:
    st.session_state.joined = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "splash_done" not in st.session_state:
    st.session_state.splash_done = False

# ---------- LOADING SPLASH SCREEN (ek dafa har session mein) ----------
if not st.session_state.splash_done:
    st.markdown(
        """
        <div class="splash-wrap">
            <div class="splash-crown">👑</div>
            <div class="splash-text">Badshah Ka Wazeer Kon Load Ho Raha Hai...</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    time.sleep(1.5)
    st.session_state.splash_done = True
    st.rerun()

# ---------- LOGIN / SIGNUP GATE ----------
if not st.session_state.logged_in:
    st.markdown(
        """
        <div class="login-header-wrap">
            <div class="login-crown">👑</div>
            <div class="login-title">Badshah Ka Wazeer Kon</div>
            <div class="login-subtitle">APNA ACCOUNT BANAO YA LOGIN KARO</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_login, tab_signup = st.tabs(["🔐  Login", "📝  Sign Up"])

    with tab_login:
        login_email = st.text_input("Email", key="login_email", placeholder="you@example.com")
        login_password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
        if st.button("Login", key="login_btn", use_container_width=True):
            if login_email.strip() == "" or login_password.strip() == "":
                st.error("Email aur password dono likho!")
            else:
                with st.spinner("Login ho raha hai..."):
                    success, result = sign_in(login_email.strip(), login_password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_email = result["email"]
                    st.session_state.uid = result["localId"]
                    st.rerun()
                else:
                    st.error(f"Login fail hua: {result}")

    with tab_signup:
        signup_email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
        signup_password = st.text_input("Password (kam se kam 6 characters)", type="password", key="signup_password", placeholder="••••••••")
        if st.button("Account Banao", key="signup_btn", use_container_width=True):
            if signup_email.strip() == "" or signup_password.strip() == "":
                st.error("Email aur password dono likho!")
            elif len(signup_password) < 6:
                st.error("Password kam se kam 6 characters ka hona chahiye!")
            else:
                with st.spinner("Account ban raha hai..."):
                    success, result = sign_up(signup_email.strip(), signup_password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_email = result["email"]
                    st.session_state.uid = result["localId"]
                    st.success("✅ Account ban gaya!")
                    st.rerun()
                else:
                    st.error(f"Signup fail hua: {result}")

    st.stop()

st.title("👑 Badshah Ka Wazeer Kon")

# ---------- PROFILE BUTTON (circular avatar khud clickable hai, center mein) ----------
if not st.session_state.joined:
    col_left, profile_col, col_right = st.columns([1, 1, 1])
    with profile_col:
        profiles = load_profiles()
        current_name = st.session_state.player_name.strip()
        has_picture = bool(current_name and current_name in profiles)

        if has_picture:
            st.markdown(
                f"""
                <style>
                div[data-testid="stPopover"] button {{
                    background-image: url("data:image/png;base64,{profiles[current_name]}") !important;
                    background-size: cover !important;
                    background-position: center !important;
                    background-repeat: no-repeat !important;
                    background-color: transparent !important;
                    border: 2px solid #FFD700 !important;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
            popover_label = " "
        else:
            st.markdown(
                """
                <style>
                div[data-testid="stPopover"] button {
                    border: 2px solid #FFD700 !important;
                    background: rgba(0,0,0,0.4) !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            popover_label = "👤"

        st.markdown(
            '<div style="display:flex; flex-direction:column; align-items:center; width:100%;">',
            unsafe_allow_html=True
        )

        profile_ui = st.popover(popover_label) if hasattr(st, "popover") else st.expander("👤 Profile")

        display_name = current_name if current_name else "Profile"
        st.markdown(
            f'<div class="profile-avatar-label">{display_name}</div></div>',
            unsafe_allow_html=True
        )

        with profile_ui:
            st.write("**Apni Profile Edit Karo**")
            st.caption(f"Logged in as: {st.session_state.get('user_email', '')}")

            profile_name = st.text_input(
                "Apna Naam",
                value=st.session_state.player_name,
                key="profile_name_field"
            )

            existing_profiles = load_profiles()
            if profile_name.strip() in existing_profiles:
                st.image(
                    base64.b64decode(existing_profiles[profile_name.strip()]),
                    width=80,
                    caption="Current picture"
                )

            uploaded_pic = st.file_uploader(
                "Profile Picture Upload Karo",
                type=["png", "jpg", "jpeg"],
                key="profile_pic_field"
            )

            if st.button("💾 Save Profile", key="save_profile_btn"):
                if profile_name.strip() == "":
                    st.error("Pehle apna naam likho!")
                else:
                    st.session_state.player_name = profile_name.strip()
                    if uploaded_pic is not None:
                        save_profile_picture(profile_name.strip(), uploaded_pic.getvalue())
                    st.success("✅ Profile save ho gayi!")
                    st.rerun()

            # ---------- ADMIN PANEL LINK (sirf admin emails ko dikhega) ----------
            if st.session_state.get("user_email") in ADMIN_EMAILS:
                st.divider()
                st.page_link("pages/1_Control_Panel_x7z9.py", label="🛡️ Admin Panel")

            st.divider()
            if st.button("🚪 Logout", key="logout_btn"):
                st.session_state.logged_in = False
                st.session_state.player_name = ""
                st.rerun()

# Agar player abhi tak room mein nahi hai, to Home page dikhao
if not st.session_state.joined:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Naya Room Banao")
        room_name_input = st.text_input("Room Name", key="room_name_input")
        if st.button("Create Room"):
            if st.session_state.player_name.strip() == "":
                st.error("Pehle Profile set karo (naam likho)!")
            elif room_name_input.strip() == "":
                st.error("Room ka naam likho!")
            else:
                room_code = create_room(st.session_state.player_name, room_name_input.strip())
                st.session_state.room_code = room_code
                st.session_state.joined = True
                st.rerun()

    with col2:
        st.subheader("Room Join Karo")
        room_code_input = st.text_input("Room Code")
        if st.button("Join Room"):
            if st.session_state.player_name.strip() == "":
                st.error("Pehle Profile set karo (naam likho)!")
            elif room_code_input.strip() == "":
                st.error("Room code likho!")
            else:
                success, message = join_room(room_code_input.upper(), st.session_state.player_name)
                if success:
                    st.session_state.room_code = room_code_input.upper()
                    st.session_state.joined = True
                    st.rerun()
                else:
                    st.error(message)

# Agar player room mein join ho chuka hai
else:
    room = get_room(st.session_state.room_code)

    st.markdown(
        f'<div class="room-name-title">{room.get("room_name", "Room")}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="text-align:center; color:#FFF8DC; margin-bottom:14px;">Room Code: <b>{st.session_state.room_code}</b></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f"Aapka naam: {get_avatar_html(st.session_state.player_name)} **{st.session_state.player_name}**",
        unsafe_allow_html=True
    )

    st.subheader("Connected Players:")
    for p in room["players"]:
        st.markdown(f"{get_avatar_html(p)} **{p}**", unsafe_allow_html=True)

    st.write(f"({len(room['players'])}/4 players joined)")

    # ---------- SMART AUTO-REFRESH ----------
    should_autorefresh = True
    if room.get("game_started", False):
        _phase = room.get("phase", "role_reveal")
        if _phase == "role_reveal":
            _badshah_check, _wazeer_check = get_reveal_info(st.session_state.room_code)
            if st.session_state.player_name == _wazeer_check:
                should_autorefresh = False

    if should_autorefresh:
        st_autorefresh(interval=10000, key="room_autorefresh")

    if not room.get("game_started", False):
        if check_and_start_game(st.session_state.room_code):
            st.rerun()

    if room.get("game_started", False):

        phase = room.get("phase", "role_reveal")

        if phase == "game_over":
            st.balloons()
            st.header("🏁 Game Khatam!")

            winners, max_score = get_winner(st.session_state.room_code)

            if len(winners) == 1:
                st.success(f"🏆 Winner: {get_avatar(winners[0])} **{winners[0]}** ({max_score} points)")
            else:
                winner_display = ", ".join([f"{get_avatar(w)} {w}" for w in winners])
                st.success(f"🏆 Winners (Tie): {winner_display} ({max_score} points)")

            st.divider()
            st.subheader("📊 Final Leaderboard")
            scores = get_scores(st.session_state.room_code)
            for rank, (player, score) in enumerate(sorted(scores.items(), key=lambda x: -x[1]), start=1):
                st.markdown(
                    f"**#{rank}.** {get_avatar_html(player)} **{player}**: {score} points",
                    unsafe_allow_html=True
                )

        else:
            st.write(f"### Round {room['current_round']} / {room['total_rounds']}")

            my_role = get_player_role(st.session_state.room_code, st.session_state.player_name)

            style = get_role_style(my_role)

            card_html = f"""
            <style>
            .card-container {{
                perspective: 1000px;
                width: 220px;
                height: 300px;
                margin: 20px auto;
            }}
            .card {{
                width: 100%;
                height: 100%;
                position: relative;
                transform-style: preserve-3d;
                animation: flipIn 1.2s ease-out;
            }}
            @keyframes flipIn {{
                from {{ transform: rotateY(180deg); opacity: 0; }}
                to {{ transform: rotateY(0deg); opacity: 1; }}
            }}
            .card-face {{
                position: absolute;
                width: 100%;
                height: 100%;
                backface-visibility: hidden;
                border-radius: 16px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                box-shadow: 0 8px 20px rgba(0,0,0,0.4);
            }}
            .card-front {{
                background: {style['bg']};
                border: 3px solid {style['color']};
            }}
            .role-emoji {{
                font-size: 70px;
                margin-bottom: 10px;
            }}
            .role-name {{
                font-size: 28px;
                font-weight: bold;
                color: {style['color']};
                font-family: sans-serif;
            }}
            </style>

            <div class="card-container">
                <div class="card">
                    <div class="card-face card-front">
                        <div class="role-emoji">{style['emoji']}</div>
                        <div class="role-name">{my_role}</div>
                    </div>
                </div>
            </div>
            """

            components.html(card_html, height=340)

            st.divider()

            badshah_name, wazeer_name = get_reveal_info(st.session_state.room_code)
            st.subheader("👀 Reveal Phase")
            st.markdown(f"👑 **Badshah:** {get_avatar_html(badshah_name)} {badshah_name}", unsafe_allow_html=True)
            st.markdown(f"🧠 **Wazeer:** {get_avatar_html(wazeer_name)} {wazeer_name}", unsafe_allow_html=True)

            st.divider()

            if phase == "role_reveal":
                hidden_players = get_hidden_players(st.session_state.room_code)

                st.subheader("🕵️ Guessing Phase")

                if st.session_state.player_name == wazeer_name:
                    st.write("Aapko decide karna hai: in mein se **Chor** kaun hai?")
                    guess_choice = st.radio(
                        "Apna guess chuno:",
                        hidden_players,
                        format_func=lambda p: f"{get_avatar(p)} {p}"
                    )

                    if st.button("Guess Submit Karo"):
                        submit_guess(st.session_state.room_code, guess_choice)
                        st.rerun()
                else:
                    st.info(f"⏳ Wazeer ({get_avatar(wazeer_name)} {wazeer_name}) apna guess bana rahe hain...")
                    if st.button("Refresh"):
                        st.rerun()

            elif phase == "result":
                st.subheader("🏆 Result")

                correct = is_guess_correct(st.session_state.room_code)
                guessed = room.get("wazeer_guess")

                st.write(f"Wazeer ne guess kiya:")
                st.markdown(f"{get_avatar_html(guessed)} **{guessed}**", unsafe_allow_html=True)

                if correct:
                    st.success("✅ Sahi guess! Wazeer ne Chor ko pehchaan liya!")
                else:
                    st.error("❌ Galat guess! Chor bach gaya!")

                st.write("**Sab ke asli roles:**")
                for player, role in room["roles"].items():
                    st.markdown(f"{get_avatar_html(player)} **{player}**: {role}", unsafe_allow_html=True)

                if not room.get("scores_calculated", False):
                    calculate_scores(st.session_state.room_code, correct)
                    room["scores_calculated"] = True
                    save_room(st.session_state.room_code, room)

                st.divider()
                st.subheader("📊 Scoreboard")
                scores = get_scores(st.session_state.room_code)
                for player, score in sorted(scores.items(), key=lambda x: -x[1]):
                    st.markdown(f"{get_avatar_html(player)} **{player}**: {score} points", unsafe_allow_html=True)

                st.divider()

                if st.button("➡️ Next Round"):
                    start_next_round(st.session_state.room_code)
                    st.rerun()
    else:
        if st.button("Refresh"):
            st.rerun()