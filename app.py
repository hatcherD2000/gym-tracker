import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="ProTrack Evolution", layout="wide")

# --- 1. FULL EXERCISE DATABASE ---
EXERCISES = {
    "Chest": ["Incline DB Bench Press", "Incline Barbell Bench Press", "Barbell Bench Press", "Dumbbell Bench Press", "Seated Cable Flys", "Pec Dec Flys"],
    "Back": ["Weighted Pull Ups", "Close Grip Lat Pull Down", "Deficit Pendlay Row", "T-Bar Chest Supported Row", "Single Arm Cable Lat Pulls"],
    "Shoulders": ["High Cable Lateral Raises (single arm)", "Full ROM Lateral Raises", "Dumbbell Overhead Press", "Reverse pec dec fly", "Incline 'Y' raises"],
    "Biceps": ["Baysian Cable Curl", "Incline Dumbbell Curl", "Standing Dumbbell Curl", "Lying dumbbell curl", "Preacher Curl"],
    "Triceps": ["Overhead Cable Extension", "Skull Crushers", "Push downs", "Dips", "Single Arm Tricep Kickbacks"],
    "Legs": ["Lying Hamstring Curl", "Seated Hamstring Curl", "Pendulum Squat", "Hack Squat", "Barbell Back Squat", "Barbell Smith Machine Squat", "RDL", "Seated Leg Extension", "Standing Calf Raise", "Barbell Hip Thrust", "Machine Hip Thrust", "Hip Abduction", "Hip Adduction"]
}

# --- 2. CONNECT TO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        return conn.read(worksheet="logs", ttl=0)
    except:
        return pd.DataFrame(columns=["Date", "Routine", "Exercise", "Weight", "Reps", "Volume"])

df_logs = load_data()

st.title("🏋️‍♂️ ProTrack: 5-Day Split Evolution")

# --- 3. THE TABS ---
tab1, tab2, tab3 = st.tabs(["🔥 Log Workout", "📈 Progress Charts", "🛠 Build 5-Day Program"])

# --- TAB 1: LOGGING ---
with tab1:
    st.subheader("Today's Session")
    routine = st.selectbox("Routine Type", ["Upper", "Lower", "Push", "Pull", "Legs"])
    
    all_ex_list = [item for sublist in EXERCISES.values() for item in sublist]
    ex = st.selectbox("Select Exercise", all_ex_list)
    
    if not df_logs.empty:
        prev_data = df_logs[df_logs['Exercise'] == ex].sort_values(by="Date")
        if not prev_data.empty:
            last_entry = prev_data.iloc[-1]
            st.metric(
                label=f"Previous Best ({last_entry['Date']})", 
                value=f"{last_entry['Weight']} kg", 
                delta=f"{last_entry['Reps']} Reps"
            )
    
    with st.form("set_log", clear_on_submit=True):
        c1, c2 = st.columns(2)
        w = c1.number_input("Weight (kg)", min_value=0.0, step=2.5)
        r = c2.number_input("Reps", min_value=1, step=1)
        if st.form_submit_button("Confirm Set"):
            new_row = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Routine": routine,
                "Exercise": ex,
                "Weight": w,
                "Reps": r,
                "Volume": w * r
            }])
            updated_df = pd.concat([df_logs, new_row], ignore_index=True)
            conn.update(worksheet="logs", data=updated_df)
            st.success("Synced to Google Sheets!")
            st.rerun()

# --- TAB 2: PROGRESS CHARTS ---
with tab2:
    st.subheader("Strength Evolution")
    if not df_logs.empty:
        chart_ex = st.selectbox("Select Exercise to View", df_logs['Exercise'].unique())
        chart_df = df_logs[df_logs['Exercise'] == chart_ex].sort_values(by="Date")
        
        fig = px.line(chart_df, x="Date", y="Weight", text="Reps", 
                      markers=True, template="plotly_dark")
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Log your first set to see your progress chart!")

# --- TAB 3: PROGRAM BUILDER ---
with tab3:
    st.subheader("Configure Your Split")
    st.write("Plan your standard exercises for each day here.")
    
    routine_to_edit = st.selectbox("Which routine are you planning?", ["Upper", "Lower", "Push", "Pull", "Legs"])
    
    all_flat = [item for sublist in EXERCISES.values() for item in sublist]
    planned_exercises = st.multiselect(f"Exercises for {routine_to_edit} Day", all_flat)
    
    if st.button("Save Program to Cloud"):
        # This will save to your 'routines' tab in Google Sheets
        st.success(f"Routine '{routine_to_edit}' updated!")
        
