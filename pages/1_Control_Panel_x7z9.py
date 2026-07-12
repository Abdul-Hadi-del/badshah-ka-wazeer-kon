import streamlit as st
import firebase_admin
from firebase_admin import auth as fb_auth
from firebase_service import db
from config import ADMIN_EMAILS

st.set_page_config(page_title="Admin Portal", page_icon="🛡️", layout="wide")

# ---------- ACCESS GUARD ----------
if not st.session_state.get("logged_in", False):
    st.error("Pehle main app se login karo.")
    st.stop()

if st.session_state.get("user_email") not in ADMIN_EMAILS:
    st.error("🚫 Aapko is portal ka access nahi hai.")
    st.stop()

st.title("🛡️ Admin Portal")
st.caption(f"Logged in as: {st.session_state.user_email}")

tab_rooms, tab_users = st.tabs(["🎮 Rooms", "👥 Users"])

# ---------- ROOMS TAB ----------
with tab_rooms:
    st.subheader("Active Rooms")

    rooms_docs = list(db.collection("rooms").stream())

    if not rooms_docs:
        st.info("Koi room abhi active nahi hai.")
    else:
        for doc in rooms_docs:
            room = doc.to_dict()
            room_code = doc.id

            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.markdown(f"**{room.get('room_name', 'Untitled')}** — `{room_code}`")
                    st.write(f"Players: {', '.join(room.get('players', []))}")

                with col2:
                    status = "🟢 Started" if room.get("game_started") else "⚪ Waiting"
                    st.write(status)
                    st.write(f"Round {room.get('current_round', '-')} / {room.get('total_rounds', '-')}")
                    st.write(f"Phase: {room.get('phase', '-')}")

                with col3:
                    if st.button("🗑️ Delete", key=f"del_{room_code}"):
                        db.collection("rooms").document(room_code).delete()
                        st.rerun()

        st.divider()
        if st.button("🧹 Delete All Rooms"):
            for doc in rooms_docs:
                db.collection("rooms").document(doc.id).delete()
            st.rerun()

# ---------- USERS TAB ----------
with tab_users:
    st.subheader("Registered Users")

    try:
        users = fb_auth.list_users().iterate_all()
        user_list = list(users)

        st.write(f"Total users: **{len(user_list)}**")

        for user in user_list:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"📧 {user.email}")
                    st.caption(f"UID: {user.uid}")
                with col2:
                    st.write(f"Verified: {'✅' if user.email_verified else '❌'}")
                with col3:
                    if st.button("🗑️ Delete", key=f"deluser_{user.uid}"):
                        fb_auth.delete_user(user.uid)
                        st.rerun()
    except Exception as e:
        st.error(f"Users list nahi la saka: {e}")