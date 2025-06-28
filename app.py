import streamlit as st
import json
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# --- Config ---
ADMIN_USERNAME = "Creator"
ADMIN_PASSWORD = "Dhruv@123"  # Change this!
USER_ROLES = ["Creator", "AI Developer Intern"]
PROGRESS_FILE = Path("progress.json")
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --- Helpers ---
def load_progress():
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

def get_today():
    now = datetime.now()
    return now.strftime("%Y-%m-%d"), now.strftime("%A")

def export_csv(progress):
    rows = []
    for intern, days in progress.items():
        for date, entry in days.items():
            rows.append({
                "Intern Name": intern,
                "Date": date,
                "Day": entry["day"],
                "Progress": entry["progress"]
            })
    df = pd.DataFrame(rows)
    return df

# --- Custom CSS for more color and animation ---
st.markdown("""
    <style>
    .stApp {background: linear-gradient(120deg, #f5d6e6 0%, #c3cfe2 100%); animation: bgmove 10s infinite alternate;}
    @keyframes bgmove {0%{background-position:0 0;} 100%{background-position:100% 100%;}}
    .big-title {font-size: 3em; font-weight: bold; color: #6a0572; text-align: center; margin-bottom: 0.5em; text-shadow: 2px 2px 8px #fff3e6;}
    .progress-box {background: #fff3e6cc; border-radius: 1em; padding: 1.5em; margin-bottom: 1em; box-shadow: 0 4px 24px #e0c3fc55; transition: box-shadow 0.5s;}
    .progress-box:hover {box-shadow: 0 8px 32px #6a057299;}
    .admin-section {background: #e0c3fcdd; border-radius: 1em; padding: 1.5em; margin-top: 2em;}
    .red-dot {height: 16px; width: 16px; background-color: #e74c3c; border-radius: 50%; display: inline-block; margin-right: 8px;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">Team Progress Tracker</div>', unsafe_allow_html=True)

if 'progress' not in st.session_state:
    st.session_state['progress'] = load_progress()

# --- User selection ---
st.sidebar.title("Login")
role = st.sidebar.selectbox("I am a...", USER_ROLES)

# --- AI Developer Intern login ---
if role == "AI Developer Intern":
    name = st.sidebar.text_input("Enter your name:")
    if name.strip():
        today_date, today_day = get_today()
        st.markdown(f"<h3 style='color:#6a0572;'>Welcome AI Developer Intern!</h3>", unsafe_allow_html=True)
        st.markdown(f"### Welcome, {name}!")
        st.markdown(f"**Today:** {today_day}, {today_date}")
        st.markdown('<div class="progress-box">', unsafe_allow_html=True)
        progress = st.session_state['progress']
        already_submitted = (
            name in progress and today_date in progress[name]
        )
        if already_submitted:
            st.success("You have already submitted your progress for today.")
            st.info(f"**Your progress:** {progress[name][today_date]['progress']}")
        else:
            prog = st.text_area("Enter your progress for today:")
            if st.button("Submit Progress"):
                if name not in progress:
                    progress[name] = {}
                progress[name][today_date] = {"day": today_day, "progress": prog}
                save_progress(progress)
                st.success("Progress submitted!")
        st.markdown('</div>', unsafe_allow_html=True)
        st.balloons()
    else:
        st.info("Please enter your name to continue.")

# --- Creator (admin) login ---
if role == ADMIN_USERNAME:
    admin_authenticated = False
    admin_password = st.sidebar.text_input("Enter admin password:", type="password")
    if st.sidebar.button("Login as Admin"):
        if admin_password == ADMIN_PASSWORD:
            st.session_state['admin_authenticated'] = True
            st.sidebar.success("Admin login successful!")
        else:
            st.session_state['admin_authenticated'] = False
            st.sidebar.error("Incorrect password.")
    admin_authenticated = st.session_state.get('admin_authenticated', False)
    if admin_authenticated:
        st.markdown("<h3 style='color:#6a0572;'>Welcome TechLead!</h3>", unsafe_allow_html=True)
        st.markdown('<div class="admin-section">', unsafe_allow_html=True)
        st.markdown("## 👑 Admin Dashboard")
        progress = st.session_state['progress']
        today_date, today_day = get_today()
        # List of all interns
        interns = sorted(progress.keys())
        # Table of all progress
        rows = []
        for intern in interns:
            for date, entry in progress[intern].items():
                rows.append({
                    "Intern Name": intern,
                    "Date": date,
                    "Day": entry["day"],
                    "Progress": entry["progress"]
                })
        df = pd.DataFrame(rows)
        st.markdown("### All Progress Records")
        st.dataframe(df.sort_values(["Date", "Intern Name"], ascending=[False, True]), use_container_width=True)
        # Export
        csv_df = export_csv(progress)
        st.download_button(
            label="Export as CSV",
            data=csv_df.to_csv(index=False).encode('utf-8'),
            file_name="team_progress.csv",
            mime="text/csv"
        )
        # Visual indicator for missing progress
        st.markdown("### Today's Submissions")
        for intern in interns:
            submitted = today_date in progress[intern]
            dot = '<span class="red-dot"></span>' if not submitted else ''
            st.markdown(f"{dot}<b>{intern}</b>: {progress[intern][today_date]['progress'] if submitted else 'No update yet'}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.snow()
    elif admin_password:
        st.warning("Please enter the correct admin password to view the dashboard.")

# --- Animated/Colorful Overview (for all users) ---
st.markdown("---")
st.markdown("## 🌟 Team Progress Overview (Current Day)")
today_date, today_day = get_today()
progress = st.session_state['progress']
def has_any_progress(user_progress):
    return any(
        isinstance(v, dict) and 'progress' in v and str(v['progress']).strip()
        for v in user_progress.values()
    )
all_names = [name for name, prog in progress.items() if name and has_any_progress(prog)]
for real_name in all_names:
    prog = progress[real_name][today_date]['progress'] if today_date in progress[real_name] else ""
    color = f"hsl({(all_names.index(real_name)*30)%360}, 80%, 80%)"
    st.markdown(f'<div style="background:{color};border-radius:0.5em;padding:0.5em 1em;margin-bottom:0.5em;"> <b>{real_name}:</b> {prog or "<i>No update yet</i>"} </div>', unsafe_allow_html=True)
# Animated bar chart for team completion (today)
st.markdown("### Team Progress Completion (Today)")
bar_colors = ["#6a0572" if today_date in progress[rn] and progress[rn][today_date]['progress'].strip() else "#e0c3fc" for rn in all_names]
bar_fig = go.Figure(go.Bar(
    x=all_names,
    y=[1 if today_date in progress[rn] and progress[rn][today_date]['progress'].strip() else 0 for rn in all_names],
    marker_color=bar_colors,
    text=["Done" if today_date in progress[rn] and progress[rn][today_date]['progress'].strip() else "Pending" for rn in all_names],
    textposition="outside"
))
bar_fig.update_layout(
    yaxis=dict(showticklabels=False, range=[0,1.2]),
    xaxis_tickangle=-45,
    height=400,
    plot_bgcolor='#fff3e6',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=40, b=80)
)
st.plotly_chart(bar_fig, use_container_width=True) 
