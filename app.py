import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ProTrack Architect", layout="wide")

# --- 1. THE EXERCISE MASTER LIST ---
# (Shortened for brevity here, but keep your full list in your version!)
EXERCISES = {
    "Chest": ["Incline DB Bench Press", "Incline Barbell Bench Press", "Barbell Bench Press", "Dumbbell Bench Press", "Seated Cable Flys", "Pec Dec Flys"],
    "Back": ["Weighted Pull Ups", "Close Grip Lat Pull Down", "Deficit Pendlay Row", "T-Bar Chest Supported Row", "Single Arm Cable Lat Pulls"],
    "Shoulders": ["High Cable Lateral Raises (single arm)", "Full ROM Lateral Raises", "Dumbbell Overhead Press", "Reverse pec dec fly", "Incline 'Y' raises"],
    "Biceps": ["Baysian Cable Curl", "Incline Dumbbell Curl", "Standing Dumbbell Curl", "Lying dumbbell curl", "Preacher Curl"],
    "Triceps": ["Overhead Cable Extension", "Skull Crushers", "Push downs", "Dips", "Single Arm Tricep Kickbacks"],
    "Legs": ["Lying Hamstring Curl", "Seated Hamstring Curl", "Pendulum Squat", "Hack Squat", "Barbell Back Squat", "Barbell Smith Machine Squat", "RDL", "Seated Leg Extension", "Standing Calf Raise", "Barbell Hip Thrust", "Machine Hip Thrust", "Hip Abduction", "Hip Adduction"]
}

# --- 2. INITIALIZE STORAGE ---
if 'my_routines' not in st.session_state:
    st.session_state.my_routines = {} # Format: {"Leg Day": ["RDL", "Hack Squat"]}
if 'workout_log' not in st.session_state:
    st.session_state.workout_log = []

# --- 3. APP NAVIGATION ---
st.title("🏋️‍♂️ ProTrack Architect")
menu = st.sidebar.radio("Navigation", ["Run Workout", "Build Routine", "History"])

# --- BUILDER SECTION ---
if menu == "Build Routine":
    st.header("🛠 Routine Builder")
    new_routine_name = st.text_input("Routine Name", placeholder="e.g. Push Day A")
    
    # Select multiple exercises from your list
    all_ex_flat = [item for sublist in EXERCISES.values() for item in sublist]
    selected_exs = st.multiselect("Select Exercises", all_ex_flat)
    
    if st.button("Save Routine"):
        if new_routine_name and selected_exs:
            st.session_state.my_routines[new_routine_name] = selected_exs
            st.success(f"Routine '{new_routine_name}' saved!")
        else:
            st.error("Please provide a name and at least one exercise.")

# --- RUN WORKOUT SECTION ---
elif menu == "Run Workout":
    st.header("🚀 Start Training")
    if not st.session_state.my_routines:
        st.warning("No routines found. Go to 'Build Routine' first!")
    else:
        chosen_routine = st.selectbox("Choose a Routine", list(st.session_state.my_routines.keys()))
        routine_exercises = st.session_state.my_routines[chosen_routine]
        
        # Display exercises for the workout
        st.info(f"Today's Plan: {', '.join(routine_exercises)}")
        
        # Logging Form
        with st.form("set_logger", clear_on_submit=True):
            ex = st.selectbox("Exercise to log", routine_exercises)
            c1, c2 = st.columns(2)
            w = c1.number_input("Weight (kg)", step=2.5)
            r = c2.number_input("Reps", step=1)
            if st.form_submit_button("Log Set"):
                st.session_state.workout_log.append({
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Routine": chosen_routine,
                    "Exercise": ex,
                    "Weight": w,
                    "Reps": r
                })
                st.toast(f"Logged {ex}!")

# --- HISTORY SECTION ---
elif menu == "History":
    st.header("📜 Training History")
    if st.session_state.workout_log:
        df = pd.DataFrame(st.session_state.workout_log)
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download History", csv, "gym_history.csv", "text/csv")
    else:
        st.write("No history recorded yet.")
        
