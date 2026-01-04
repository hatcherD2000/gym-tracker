import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="ProTrack Evolution", layout="wide")

# --- 1. PRESET WORKOUTS ---
PRESETS = {
    "Push (Chest/Shoulders/Tri)": [
        "Barbell Bench Press", "Incline DB Bench Press", 
        "Dumbbell Overhead Press", "High Cable Lateral Raises (single arm)", 
        "Push downs", "Dips"
    ],
    "Pull (Back/Biceps)": [
        "Weighted Pull Ups", "Close Grip Lat Pull Down", 
        "Deficit Pendlay Row", "Baysian Cable Curl", "Preacher Curl"
    ],
    "Legs": [
        "Barbell Back Squat", "RDL", "Hack Squat", 
        "Seated Leg Extension", "Lying Hamstring Curl"
    ]
}

# --- 2. DATA PERSISTENCE ---
# This looks for an existing file to load your progress
FILE_NAME = "workout_history.csv"

if 'history' not in st.session_state:
    if os.path.exists(FILE_NAME):
        st.session_state.history = pd.read_csv(FILE_NAME).to_dict('records')
    else:
        st.session_state.history = []

def save_data():
    df = pd.DataFrame(st.session_state.history)
    df.to_csv(FILE_NAME, index=False)

# --- 3. UI LAYOUT ---
st.title("🏋️‍♂️ ProTrack Evolution")

tab1, tab2, tab3 = st.tabs(["🔥 Active Workout", "📅 Weekly Progress", "⚙️ Setup Presets"])

with tab1:
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.subheader("Select Routine")
        routine_name = st.selectbox("Which program today?", list(PRESETS.keys()))
        current_exercises = PRESETS[routine_name]
        
    with col_b:
        st.subheader(f"Logging: {routine_name}")
        ex_to_log = st.selectbox("Exercise", current_exercises)
        
        # PROGRESSION LOGIC: Show what you did last time
        if st.session_state.history:
            past_df = pd.DataFrame(st.session_state.history)
            past_perf = past_df[past_df['Exercise'] == ex_to_log]
            if not past_perf.empty:
                last_set = past_perf.iloc[-1]
                st.warning(f"Last time: {last_set['Weight']}kg x {last_set['Reps']}")

        with st.form("set_entry", clear_on_submit=True):
            c1, c2 = st.columns(2)
            w = c1.number_input("Weight", min_value=0.0, step=2.5)
            r = c2.number_input("Reps", min_value=1, step=1)
            if st.form_submit_button("Log Set"):
                new_entry = {
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Routine": routine_name,
                    "Exercise": ex_to_log,
                    "Weight": w,
                    "Reps": r,
                    "Volume": w * r
                }
                st.session_state.history.append(new_entry)
                save_data() # Saves to CSV
                st.success("Set Logged!")

with tab2:
    st.subheader("Your Progress Over Time")
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        
        # Filter by exercise to see growth
        filter_ex = st.selectbox("Filter Progress by Exercise", df_hist['Exercise'].unique())
        filtered_df = df_hist[df_hist['Exercise'] == filter_ex]
        
        st.line_chart(filtered_df, x="Date", y="Weight")
        st.dataframe(filtered_df.sort_values(by="Date", ascending=False))
    else:
        st.info("No history found. Start training to see your charts!")

with tab3:
    st.info("In this section, you can eventually add or modify your preset routines.")
    st.write("Current Exercises in System:", sum(len(v) for v in PRESETS.values()))
  
