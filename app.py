import streamlit as st
import json
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd
import datetime

# --- User roles ---
USER_ROLES = ["Creator", "AI Developer Intern"]
ADMIN_USERNAME = "Creator"
ADMIN_PASSWORD = "Dhruv@123"  # Change this to your desired password
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --- Persistent storage ---
PROGRESS_FILE = Path("progress.json")

def load_progress():
    try:
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

if 'progress' not in st.session_state:
    st.session_state['progress'] = load_progress()

# --- Custom CSS for more color and animation ---
st.markdown("""
    <style>
    .stApp {background: linear-gradient(120deg, #f5d6e6 0%, #c3cfe2 100%); animation: bgmove 10s infinite alternate;}
    @keyframes bgmove {0%{background-position:0 0;} 100%{background-position:100% 100%;}}
    .big-title {font-size: 3em; font-weight: bold; color: #6a0572; text-align: center; margin-bottom: 0.5em; text-shadow: 2px 2px 8px #fff3e6;}
    .progress-box {background: #fff3e6cc; border-radius: 1em; padding: 1.5em; margin-bottom: 1em; box-shadow: 0 4px 24px #e0c3fc55; transition: box-shadow 0.5s;}
    .progress-box:hover {box-shadow: 0 8px 32px #6a057299;}
    .admin-section {background: #e0c3fcdd; border-radius: 1em; padding: 1.5em; margin-top: 2em;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">Team Progress Tracker</div>', unsafe_allow_html=True)

# --- User selection ---
st.sidebar.title("Login")
role = st.sidebar.selectbox("I am a...", USER_ROLES)

# --- AI Developer Intern login ---
if role == "AI Developer Intern":
    name = st.sidebar.text_input("Enter your name:")
    if name.strip():
        st.markdown(f"<h3 style='color:#6a0572;'>Welcome AI Developer Intern!</h3>", unsafe_allow_html=True)
        st.markdown(f"### Welcome, {name}!")
        st.markdown('<div class="progress-box">', unsafe_allow_html=True)
        today = datetime.datetime.now().strftime("%A")
        progress = st.session_state['progress']
        if name not in progress:
            progress[name] = {day: "" for day in DAYS_OF_WEEK}
        prog_val = progress[name].get(today, "")
        progress_input = st.text_area(f"Your Progress for {today}", value=prog_val)
        if st.button("Update Progress"):
            progress[name][today] = progress_input
            save_progress(dict(progress))
            st.toast("✅ Progress updated!", icon="✅")
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
        st.markdown("## 👑 Admin Dashboard (Private)")
        st.markdown("### Team Weekly Progress Overview:")
        progress = st.session_state['progress']
        all_names = list(progress.keys())
        for real_name in all_names:
            st.markdown(f"#### {real_name}")
            for day in DAYS_OF_WEEK:
                val = progress[real_name].get(day, "")
                new_val = st.text_area(f"{real_name} - {day}", value=val, key=f"admin_{real_name}_{day}")
                if st.button(f"Update {real_name} - {day}", key=f"btn_{real_name}_{day}"):
                    progress[real_name][day] = new_val
                    save_progress(dict(progress))
                    st.toast(f"✅ Updated {real_name} - {day}", icon="✅")
        st.markdown('</div>', unsafe_allow_html=True)
        st.snow()
        # Confetti if all members have updated all days
        if all(all(progress[rn][d].strip() for d in DAYS_OF_WEEK) for rn in all_names):
            st.success("🎉 All members have updated their weekly progress!")
        # Team completion chart (number of members who updated all days)
        completed = sum(1 for rn in all_names if all(progress[rn][d].strip() for d in DAYS_OF_WEEK))
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = completed,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Members with Full Weekly Progress"},
            gauge = {
                'axis': {'range': [0, len(all_names)]},
                'bar': {'color': "#6a0572"},
                'steps' : [
                    {'range': [0, len(all_names)//2], 'color': "#f5d6e6"},
                    {'range': [len(all_names)//2, len(all_names)], 'color': "#c3cfe2"}
                ],
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
    elif admin_password:
        st.warning("Please enter the correct admin password to view the dashboard.")

# --- Animated/Colorful Overview (for all users) ---
st.markdown("---")
st.markdown("## 🌟 Team Progress Overview (Current Day)")
today = datetime.datetime.now().strftime("%A")
progress = st.session_state['progress']
# Only show real names with at least one progress record
def has_any_progress(user_progress):
    return any(v.strip() for v in user_progress.values())
all_names = [name for name, prog in progress.items() if name and has_any_progress(prog)]
for real_name in all_names:
    prog = progress[real_name].get(today, "")
    color = f"hsl({(all_names.index(real_name)*30)%360}, 80%, 80%)"
    st.markdown(f'<div style="background:{color};border-radius:0.5em;padding:0.5em 1em;margin-bottom:0.5em;"> <b>{real_name}:</b> {prog or "<i>No update yet</i>"} </div>', unsafe_allow_html=True)
# Animated bar chart for team completion (today)
st.markdown("### Team Progress Completion (Today)")
bar_colors = ["#6a0572" if progress[rn].get(today, "").strip() else "#e0c3fc" for rn in all_names]
bar_fig = go.Figure(go.Bar(
    x=all_names,
    y=[1 if progress[rn].get(today, "").strip() else 0 for rn in all_names],
    marker_color=bar_colors,
    text=["Done" if progress[rn].get(today, "").strip() else "Pending" for rn in all_names],
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
