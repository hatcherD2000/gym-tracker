import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="ProTrack Guided Elite", layout="wide")

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

def load_all_data():
    try:
        logs = conn.read(worksheet="logs", ttl=0)
        logs['Date'] = pd.to_datetime(logs['Date'])
    except:
        logs = pd.DataFrame(columns=["Date", "Routine", "Exercise", "Weight", "Reps", "Volume", "Est1RM", "SetType"])
    
    try:
        routines = conn.read(worksheet="routines", ttl=0)
    except:
        routines = pd.DataFrame(columns=["RoutineName", "Exercise", "TargetReps", "WarmupSets", "WorkingSets", "ToFailure"])
        
    return logs, routines

df_logs, df_routines = load_all_data()

st.title("🏋️‍♂️ ProTrack: Guided 5-Day Split")

tab1, tab2, tab3 = st.tabs(["🔥 Log Workout", "📊 Strength Analytics", "🛠 Build 5-Day Program"])

# --- TAB 3: GUIDED PROGRAM BUILDER ---
with tab3:
    st.subheader("Design Your Session Recipes")
    r_to_build = st.selectbox("Which routine?", ["Upper", "Lower", "Push", "Pull", "Legs"])
    
    with st.expander(f"Add Exercise to {r_to_build}", expanded=True):
        new_ex = st.selectbox("Pick Exercise", EXERCISES)
        col_a, col_b = st.columns(2)
        target_reps = col_a.text_input("Target Rep Range", placeholder="e.g. 6-8")
        w_sets = col_b.number_input("Working Sets", min_value=1, value=3)
        
        col_c, col_d = st.columns(2)
        u_sets = col_c.number_input("Warmup Sets", min_value=0, value=1)
        failure = col_d.checkbox("Go to Failure?")
        
        if st.button("Add to Routine"):
            new_row = pd.DataFrame([{
                "RoutineName": r_to_build,
                "Exercise": new_ex,
                "TargetReps": target_reps,
                "WarmupSets": u_sets,
                "WorkingSets": w_sets,
                "ToFailure": "Yes" if failure else "No"
            }])
            # Update GSheet
            df_routines = pd.concat([df_routines, new_row], ignore_index=True)
            conn.update(worksheet="routines", data=df_routines)
            st.success(f"Added {new_ex} to {r_to_build}!")

    if not df_routines.empty:
        st.write("### Current Plan")
        st.dataframe(df_routines[df_routines['RoutineName'] == r_to_build], hide_index=True)
        if st.button("Clear Routine"):
            df_routines = df_routines[df_routines['RoutineName'] != r_to_build]
            conn.update(worksheet="routines", data=df_routines)
            st.rerun()

# --- TAB 1: LOGGING WITH TARGETS ---
with tab1:
    routine_now = st.selectbox("Select Session", ["Upper", "Lower", "Push", "Pull", "Legs"])
    
    if not df_routines.empty and routine_now in df_routines['RoutineName'].values:
        day_plan = df_routines[df_routines['RoutineName'] == routine_now]
        ex_choice = st.selectbox("Select Exercise", day_plan['Exercise'].unique())
        
        # Display the "Target" for this exercise
        target_info = day_plan[day_plan['Exercise'] == ex_choice].iloc[0]
        st.info(f"🎯 **Target:** {target_info['WorkingSets']} sets of {target_info['TargetReps']} reps. " + 
                (f"🔥 **Go to Failure!**" if target_info['ToFailure'] == "Yes" else ""))
    else:
        st.warning("Build this routine in Tab 3 first!")
        ex_choice = st.selectbox("Select Exercise", EXERCISES)

    with st.form("log_set", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        set_type = c1.selectbox("Set Type", ["Working", "Warmup", "Failure"])
        w = c2.number_input("Weight (kg)", step=2.5)
        r = c3.number_input("Reps", step=1)
        if st.form_submit_button("Confirm Set"):
            current_1rm = calculate_1rm(w, r)
            new_log = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"), 
                "Routine": routine_now, "Exercise": ex_choice, 
                "Weight": w, "Reps": r, "Volume": w*r,
                "Est1RM": current_1rm, "SetType": set_type
            }])
            updated_logs = pd.concat([df_logs, new_log], ignore_index=True)
            conn.update(worksheet="logs", data=updated_logs)
            st.success("Set saved!")
            st.rerun()

# --- TAB 2: ANALYTICS ---
with tab2:
    if not df_logs.empty:
        comp_ex = st.selectbox("Select Exercise to View", df_logs['Exercise'].unique())
        # Filter for only working sets to keep the chart clean
        working_only = df_logs[df_logs['SetType'] != "Warmup"]
        sub_df = working_only[working_only['Exercise'] == comp_ex].sort_values(by="Date")
        fig = px.line(sub_df, x="Date", y="Est1RM", title=f"1RM Trend (Working Sets): {comp_ex}", markers=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
