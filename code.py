import streamlit as st
import sqlite3
from datetime import date

# --- Setup DB ---
def init_db():
    conn = sqlite3.connect('scores.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS daily_scores (
            id INTEGER PRIMARY KEY,
            play_date TEXT UNIQUE,
            winner TEXT,
            wordle TEXT,
            connections TEXT,
            mini_crossword TEXT,
            strands TEXT
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

# --- Title ---
st.title("NYT Puzzle Scores")

# --- Add New Daily Result ---
#st.header("➕ Add Daily Winner")

with st.form("daily_form"):
    play_date = st.date_input("Date", value=date.today())
    wordle = st.selectbox("Wordle Winner", ["Jake", "Hay", "Tie"])
    connections = st.selectbox("Connections Winner", ["Jake", "Hay", "Tie"])
    mini = st.selectbox("Mini Crossword Winner", ["Jake", "Hay", "Tie"])
    strands = st.selectbox("Strands Winner", ["Jake", "Hay", "Tie"])

    submitted = st.form_submit_button("Submit")

    if submitted:
        # Count wins
        scores = {"Jake": 0, "Hay": 0}
        for result in [wordle, connections, mini, strands]:
            if result in scores:
                scores[result] += 1
        # Determine daily winner
        winner = "Tie"
        if scores["Jake"] > scores["Hay"]:
            winner = "Jake"
        elif scores["Hay"] > scores["Jake"]:
            winner = "Hay"

        try:
            conn.execute('''
                INSERT INTO daily_scores 
                (play_date, winner, wordle, connections, mini_crossword, strands)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (play_date.isoformat(), winner, wordle, connections, mini, strands))
            conn.commit()
            st.success(f"Result added! 🏆 {winner} won the day.")
        except sqlite3.IntegrityError:
            st.warning("Entry for this date already exists. Try editing the database manually.")

# --- Leaderboard ---
st.header("📊 Leaderboard")
results = conn.execute('SELECT winner, COUNT(*) FROM daily_scores GROUP BY winner').fetchall()
st.write("**Total Daily Wins**")
for winner, count in results:
    st.write(f"🏆 {winner}: {count} days")

# --- Recent Results ---
st.header("📅 Recent Days")
recent = conn.execute('''
    SELECT play_date, winner, wordle, connections, mini_crossword, strands 
    FROM daily_scores ORDER BY play_date DESC LIMIT 10
''').fetchall()

if recent:
    st.table(recent)
else:
    st.info("No results yet. Add one above!")

# --- Streak Tracker ---
st.header("🔥 Streaks")

# Fetch all winners ordered by date
rows = conn.execute('SELECT winner FROM daily_scores ORDER BY play_date').fetchall()
winners = [r[0] for r in rows]

def calculate_streaks(winners, player):
    current = longest = 0
    temp = 0
    for w in winners:
        if w == player:
            temp += 1
            longest = max(longest, temp)
        else:
            temp = 0
    current = temp
    return current, longest

for player in ["Me", "GF"]:
    current, longest = calculate_streaks(winners, player)
    st.markdown(f"**{player}** - Current Streak: 🔥 {current} | Longest Streak: 🏆 {longest}")
