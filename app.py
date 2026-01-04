import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ProTrack Pro", layout="wide")

# --- FULL EXERCISE DATABASE ---
EXERCISES = {
    "Chest": ["Incline DB Bench Press", "Incline Barbell Bench Press", "Barbell Bench Press", "Dumbbell Bench Press", "Seated Cable Flys", "Pec Dec Flys"],
    "Back": ["Weighted Pull Ups", "Close Grip Lat Pull Down", "Deficit Pendlay Row", "T-Bar Chest Supported Row", "Single Arm Cable Lat Pulls"],
    "Shoulders": ["High Cable Lateral Raises (single arm)", "Full ROM Lateral Raises", "Dumbbell Overhead Press", "Reverse pec dec fly", "Incline 'Y' raises"],
    "Biceps": ["Baysian Cable Curl", "Incline Dumbbell Curl", "Standing Dumbbell Curl", "Lying dumbbell curl", "Preacher Curl"],
    "Triceps": ["Overhead Cable Extension", "Skull Crushers", "Push downs", "Dips", "Single Arm Tricep Kickbacks"],
    "Legs": ["Lying Hamstring Curl", "Seated Hamstring Curl", "Pendulum Squat", "Hack Squat", "Barbell Back Squat", "Barbell Smith Machine Squat", "RDL", "Seated Leg Extension", "Standing Calf Raise", "Barbell Hip Thrust", "Machine Hip Thrust", "Hip Abduction", "Hip Adduction"]
}

# Temporary storage for the session (Until we connect Google Sheets)
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("🏋️‍♂️ ProTrack: Week-on-Week")

tab1, tab2 = st.tabs(["Log Workout", "Progress Tracker"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        cat = st.selectbox("Muscle Group", list(EXERCISES.keys()))
        ex = st.selectbox("Exercise", EXERCISES[cat])
    
    with col2:
        # PROGRESSION CHECK: Look for previous performance in history
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            prev = df[df['Exercise'] == ex]
            if not prev.empty:
                last_set = prev.iloc[-1]
                st.metric("Previous Lift", f"{last_set['Weight']}kg", f"{last_set['Reps']} Reps")
            else:
                st.info("First time logging this exercise!")

    with st.form("log_set", clear_on_submit=True):
        c1, c2 = st.columns(2)
        w = c1.number_input("Weight (kg)", min_value=0.0, step=2.5)
        r = c2.number_input("Reps", min_value=1, step=1)
        if st.form_submit_button("Log Set"):
            st.session_state.history.append({
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Exercise": ex, "Weight": w, "Reps": r, "Volume": w*r
            })
            st.success(f"Logged {w}kg x {r}")

with tab2:
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        st.line_chart(df_hist, x="Date", y="Weight")
        st.dataframe(df_hist)
    else:
        st.write("Start training to see progress!")
        
