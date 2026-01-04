import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ProTrack Architect", layout="wide")

# --- MASTER EXERCISE LIST ---
EXERCISES = {
    "Chest": ["Incline DB Bench Press", "Incline Barbell Bench Press", "Barbell Bench Press", "Dumbbell Bench Press", "Seated Cable Flys", "Pec Dec Flys"],
    "Back": ["Weighted Pull Ups", "Close Grip Lat Pull Down", "Deficit Pendlay Row", "T-Bar Chest Supported Row", "Single Arm Cable Lat Pulls"],
    "Shoulders": ["High Cable Lateral Raises (single arm)", "Full ROM Lateral Raises", "Dumbbell Overhead Press", "Reverse pec dec fly", "Incline 'Y' raises"],
    "Biceps": ["Baysian Cable Curl", "Incline Dumbbell Curl", "Standing Dumbbell Curl", "Lying dumbbell curl", "Preacher Curl"],
    "Triceps": ["Overhead Cable Extension", "Skull Crushers", "Push downs", "Dips", "Single Arm Tricep Kickbacks"],
    "Legs": ["Lying Hamstring Curl", "Seated Hamstring Curl", "Pendulum Squat", "Hack Squat", "Barbell Back Squat", "Barbell Smith Machine Squat", "RDL", "Seated Leg Extension", "Standing Calf Raise", "Barbell Hip Thrust", "Machine Hip Thrust", "Hip Abduction", "Hip Adduction"]
}

# --- STORAGE ---
if 'my_routines' not in st.session_state:
    st.session_state.my_routines = {}
if 'workout_log' not in st.session_state:
    st.session_state.workout_log = []

# --- TOP NAVIGATION ---
st.title("🏋️‍♂️ ProTrack Architect")
menu = st.tabs(["🚀 Run Workout", "🛠 Build Routine", "📜 History"])

# --- TAB 2: BUILDER ---
with menu[1]:
    st.header("Create a Routine")
    new_name = st.text_input("Routine Name (e.g., Push Day)")
    
    # Flatten the dictionary for the multiselect
    all_ex = [item for sublist in EXERCISES.values() for item in sublist]
    selected = st.multiselect("Pick Exercises", all_ex)
    
    if st.button("Save Routine"):
        if new_name and selected:
            st.session_state.my_routines[new_name] = selected
            st.success(f"Saved {new_name}!")
        else:
            st.error("Enter a name and pick exercises.")

# --- TAB 1: RUN WORKOUT ---
with menu[0]:
    if not st.session_state.my_routines:
        st.info("No routines found. Go to the 'Build Routine' tab to create one!")
    else:
        chosen = st.selectbox("Select Workout", list(st.session_state.my_routines.keys()))
        routine_exs = st.session_state.my_routines[chosen]
        
        with st.form("logger"):
            ex_to_log = st.selectbox("Exercise", routine_exs)
            c1, c2 = st.columns(2)
            w = c1.number_input("Weight (kg)", step=2.5)
            r = c2.number_input("Reps", step=1)
            if st.form_submit_button("Log Set"):
                st.session_state.workout_log.append({
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Routine": chosen, "Exercise": ex_to_log, "Weight": w, "Reps": r
                })
                st.toast("Saved!")

# --- TAB 3: HISTORY ---
with menu[2]:
    if st.session_state.workout_log:
        st.dataframe(pd.DataFrame(st.session_state.workout_log), use_container_width=True)
        
