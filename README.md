# Badshah Wazeer Sipahi Chor 🎭

A real-time multiplayer web game built with Python and Streamlit, bringing the classic Pakistani/South Asian party game "Badshah-Wazeer-Sipahi-Chor" to the browser.

## Live Demo

🔗 [Try it live](https://badshah-ka-wazeer-kon-knnysepksftexbvrntwlef.streamlit.app/)

## About

This project digitizes the traditional role-guessing party game where players are randomly assigned roles — King (Badshah), Minister (Wazeer), Soldier (Sipahi), and Thief (Chor) — and must use deduction and strategy to identify the Thief while scoring points based on their role.

## Features

- 🔴 Real-time multiplayer gameplay with room-based sessions
- 🎲 Random role assignment (Badshah, Wazeer, Sipahi, Chor)
- 📊 Live scoring and leaderboard tracking
- 🔥 Firebase integration for real-time data sync across players
- 🎮 Simple, browser-based interface — no installation needed for players

## Tech Stack

- **Backend/Frontend:** Python, Streamlit
- **Database & Real-time Sync:** Firebase (Firestore)
- **Authentication:** Firebase Auth

## How to Run Locally

1. Clone the repository:
```bash
   git clone https://github.com/Abdul-Hadi-del/badshah-ka-wazeer-kon.git
   cd badshah-ka-wazeer-kon
```

2. Install dependencies:
```bash
   pip install -r requirements.txt
```

3. Add your Firebase service account credentials (`firebase-service-account.json`)

4. Run the app:
```bash
   streamlit run app.py
```

## Author

**Abdul Hadi** — Software Engineering Student