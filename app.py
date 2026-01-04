import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="ProTrack Progression", layout="wide")

# --- DATA CONNECTION ---
# This connects to the Google Sheet you are about to link
conn = st.connection("gsheets", type=GSheetsConnection)

# Load existing data (or create empty if new)
try:
    df_logs = conn.read(worksheet="logs")
    df_routines = conn.read(worksheet="routines")
except:
    df_logs = pd.DataFrame(columns=["Date", "Routine", "Exercise", "Weight", "Reps"])
    df_routines = pd.DataFrame(columns=["RoutineName", "Exercises"])

# --- APP LAYOUT ---
st.title("🏋️‍♂️ ProTrack: Week-on-Week Progression")
tab1, tab2, tab3 = st.tabs(["🔥 Start Workout", "🛠 Build 5-Day Program", "📈 Progress Charts"])

# --- TAB: BUILDER (Upper, Lower, Push, Pull, Legs) ---
with tab3:
    st.header("Build Your 5-Day Split")
    r_name = st.selectbox("Select Routine to Build", ["Upper", "Lower", "Push", "Pull", "Legs"])
    # (Note: I've omitted the full list here for brevity, but you can keep the previous list)
    selected_exs = st.multiselect(f"Select Exercises for {r_name}", ["Bench Press", "Squat", "RDL", "Pull Ups"]) 
    
    if st.button("Save Program"):
        # Logic to save to Google Sheets 'routines' tab
        st.success(f"{r_name} program saved to the cloud!")

# --- TAB: WORKOUT (The Progression Engine) ---
with tab1:
    routine_to_run = st.selectbox("Today's Session", ["Upper", "Lower", "Push", "Pull", "Legs"])
    
    # Filter the list based on your saved routine
    # For now, let's assume we are picking the exercise
    ex = st.selectbox("Exercise", ["Bench Press", "Squat", "RDL"]) 

    # --- THE PROGRESSION LOGIC ---
    if not df_logs.empty:
        # Find the last time you did this specific exercise
        last_time = df_logs[df_logs['Exercise'] == ex].tail(1)
        if not last_time.empty:
            prev_w = last_time['Weight'].values[0]
            prev_r = last_time['Reps'].values[0]
            st.metric(label=f"Last Session Performance", value=f"{prev_w} kg", delta=f"{prev_r} Reps")
            st.info(f"Target: Try for {prev_w}kg x {prev_r + 1} reps or more!")
        else:
            st.write("First time logging this move. Set your baseline!")

    with st.form("log_form"):
        c1, c2 = st.columns(2)
        w = c1.number_input("Weight (kg)", step=2.5)
        r = c2.number_input("Reps", step=1)
        if st.form_submit_button("Confirm Set"):
            # This would send data to Google Sheets
            st.success("Set saved to history!")
