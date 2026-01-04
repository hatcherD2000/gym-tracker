import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="ProTrack Elite", layout="wide")

# --- MASTER LIST ---
EXERCISES = [item for sublist in {
    "C": ["Incline DB Bench Press", "Incline Barbell Bench Press", "Barbell Bench Press", "Dumbbell Bench Press", "Seated Cable Flys", "Pec Dec Flys"],
    "B": ["Weighted Pull Ups", "Close Grip Lat Pull Down", "Deficit Pendlay Row", "T-Bar Chest Supported Row", "Single Arm Cable Lat Pulls"],
    "S": ["High Cable Lateral Raises (single arm)", "Full ROM Lateral Raises", "Dumbbell Overhead Press", "Reverse pec dec fly", "Incline 'Y' raises"],
    "Bi": ["Baysian Cable Curl", "Incline Dumbbell Curl", "Standing Dumbbell Curl", "Lying dumbbell curl", "Preacher Curl"],
    "Tri": ["Overhead Cable Extension", "Skull Crushers", "Push downs", "Dips", "Single Arm Tricep Kickbacks"],
    "L": ["Lying Hamstring Curl", "Seated Hamstring Curl", "Pendulum Squat", "Hack Squat", "Barbell Back Squat", "Barbell Smith Machine Squat", "RDL", "Seated Leg Extension", "Standing Calf Raise", "Barbell Hip Thrust", "Machine Hip Thrust", "Hip Abduction", "Hip Adduction"]
}.values() for item in sublist]

# --- CONNECT TO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def calculate_1rm(w, r):
    if r <= 1: return w
    return round(w / (1.0278 - 0.0278 * r), 1)

# Safer Data Loading
def load_all_data():
    try:
        logs = conn.read(worksheet="logs", ttl=0)
        logs['Date'] = pd.to_datetime(logs['Date'])
    except:
        logs = pd.DataFrame(columns=["Date", "Routine", "Exercise", "Weight", "Reps", "Volume", "Est1RM"])
    
    try:
        routines = conn.read(worksheet="routines", ttl=0)
    except:
        routines = pd.DataFrame(columns=["RoutineName", "Exercises"])
        
    return logs, routines

df_logs, df_routines = load_all_data()

# Process Week Numbers
if not df_logs.empty:
    df_logs['Week'] = df_logs['Date'].dt.isocalendar().week
    start_week = df_logs['Week'].min()
    df_logs['Program Week'] = df_logs['Week'] - start_week + 1

st.title("🏋️‍♂️ ProTrack: Elite Progression")

tab1, tab2, tab3 = st.tabs(["🔥 Log Workout", "📊 Strength Analytics", "🛠 Program Builder"])

# --- TAB 1: LOGGING ---
with tab1:
    routine_now = st.selectbox("Current Routine", ["Upper", "Lower", "Push", "Pull", "Legs"])
    
    # Check for custom routine exercises
    if not df_routines.empty and routine_now in df_routines['RoutineName'].values:
        ex_options = df_routines[df_routines['RoutineName'] == routine_now]['Exercises'].values[0].split(",")
    else:
        ex_options = EXERCISES
    
    ex_choice = st.selectbox("Select Exercise", ex_options)

    if not df_logs.empty:
        ex_history = df_logs[df_logs['Exercise'] == ex_choice]
        if not ex_history.empty:
            max_w = ex_history['Weight'].max()
            max_1rm = ex_history['Est1RM'].max()
            c1, c2 = st.columns(2)
            c1.metric("All-Time Max Weight", f"{max_w}kg")
            c2.metric("Estimated 1RM", f"{max_1rm}kg")

    with st.form("set_log", clear_on_submit=True):
        c1, c2 = st.columns(2)
        w = c1.number_input("Weight (kg)", step=2.5)
        r = c2.number_input("Reps", step=1, min_value=1)
        if st.form_submit_button("Confirm Set"):
            current_1rm = calculate_1rm(w, r)
            new_log = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"), 
                "Routine": routine_now, 
                "Exercise": ex_choice, 
                "Weight": w, 
                "Reps": r, 
                "Volume": w*r,
                "Est1RM": current_1rm
            }])
            updated_logs = pd.concat([df_logs, new_log], ignore_index=True)
            conn.update(worksheet="logs", data=updated_logs)
            st.success(f"Logged! Est. 1RM: {current_1rm}kg")
            st.rerun()

# --- TAB 2: ANALYTICS ---
with tab2:
    if not df_logs.empty:
        comp_ex = st.selectbox("Analyze Progress:", df_logs['Exercise'].unique())
        sub_df = df_logs[df_logs['Exercise'] == comp_ex].sort_values(by="Date")
        fig = px.line(sub_df, x="Date", y=["Weight", "Est1RM"], markers=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Log your first set to unlock charts!")

# --- TAB 3: BUILDER ---
with tab3:
    r_to_build = st.selectbox("Design Routine", ["Upper", "Lower", "Push", "Pull", "Legs"])
    planned = st.multiselect(f"Exercises for {r_to_build}", EXERCISES)
    if st.button("Save Routine"):
        new_r = pd.DataFrame([{"RoutineName": r_to_build, "Exercises": ",".join(planned)}])
        # Filter out old version of this routine
        if not df_routines.empty:
            df_routines = df_routines[df_routines['RoutineName'] != r_to_build]
        df_routines = pd.concat([df_routines, new_r], ignore_index=True)
        conn.update(worksheet="routines", data=df_routines)
        st.success("Cloud Updated!")
        
