import streamlit as st
import json
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd
import datetime

# --- Demo user list ---
TEAM_MEMBERS = [f"Member {i+1}" for i in range(12)]
ADMIN_USERNAME = "Creator"
ALL_USERS = [ADMIN_USERNAME] + TEAM_MEMBERS
ADMIN_PASSWORD = "Dhruv@123"  # Change this to your desired password
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --- Persistent storage ---
PROGRESS_FILE = Path("progress.json")
NAMES_FILE = Path("member_names.json")

def load_progress():
    try:
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {user: {day: "" for day in DAYS_OF_WEEK} for user in TEAM_MEMBERS}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

def load_names():
    if NAMES_FILE.exists():
        with open(NAMES_FILE, "r") as f:
            return json.load(f)
    return {user: "" for user in TEAM_MEMBERS}

def save_names(names):
    with open(NAMES_FILE, "w") as f:
        json.dump(names, f)

if 'progress' not in st.session_state:
    st.session_state['progress'] = load_progress()
if 'member_names' not in st.session_state:
    st.session_state['member_names'] = load_names()

# --- MIGRATION: Convert old str progress to weekly dict if needed ---
progress_copy = dict(st.session_state['progress'])
today = datetime.datetime.now().strftime("%A")
for user in TEAM_MEMBERS:
    if isinstance(progress_copy.get(user, None), str):
        old_val = progress_copy[user]
        progress_copy[user] = {day: "" for day in DAYS_OF_WEEK}
        progress_copy[user][today] = old_val
st.session_state['progress'] = progress_copy
save_progress(progress_copy)

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
st.sidebar.title("Select User")
name = st.sidebar.selectbox("Who are you?", ALL_USERS)

# --- Admin password check ---
admin_authenticated = False
if name == ADMIN_USERNAME:
    admin_password = st.sidebar.text_input("Enter admin password:", type="password")
    if st.sidebar.button("Login as Admin"):
        if admin_password == ADMIN_PASSWORD:
            st.session_state['admin_authenticated'] = True
            st.sidebar.success("Admin login successful!")
        else:
            st.session_state['admin_authenticated'] = False
            st.sidebar.error("Incorrect password.")
    admin_authenticated = st.session_state.get('admin_authenticated', False)

# --- Member name entry on first login ---
if name != ADMIN_USERNAME:
    if not st.session_state['member_names'][name]:
        real_name = st.text_input("Enter your name (will be shown to admin):", key=f"realname_{name}")
        if st.button("Save Name") and real_name.strip():
            st.session_state['member_names'][name] = real_name.strip()
            save_names(dict(st.session_state['member_names']))
            st.success("Name saved! Please refresh the page or select your user again to continue with your progress update.")
        else:
            st.markdown(f"<h3 style='color:#6a0572;'>Welcome AI Developer Interns!</h3>", unsafe_allow_html=True)
            st.markdown(f"### Welcome, {st.session_state['member_names'][name]}!")
            st.markdown('<div class="progress-box">', unsafe_allow_html=True)
            today = datetime.datetime.now().strftime("%A")
            progress = st.text_area(f"Your Progress for {today}", value=st.session_state['progress'][name].get(today, ""))
            if st.button("Update Progress"):
                st.session_state['progress'][name][today] = progress
                save_progress(dict(st.session_state['progress']))
                st.toast("✅ Progress updated!", icon="✅")
            st.markdown('</div>', unsafe_allow_html=True)
            st.balloons()
# --- Admin view ---
elif admin_authenticated:
    st.markdown("<h3 style='color:#6a0572;'>Welcome TechLead!</h3>", unsafe_allow_html=True)
    st.markdown('<div class="admin-section">', unsafe_allow_html=True)
    st.markdown("## 👑 Admin Dashboard (Private)")
    st.markdown("### Team Weekly Progress Overview:")
    # Editable table for admin
    member_names = st.session_state['member_names']
    progress = st.session_state['progress']
    for member in TEAM_MEMBERS:
        st.markdown(f"#### {member_names[member] or member}")
        for day in DAYS_OF_WEEK:
            val = st.text_area(f"{member} - {day}", value=progress[member][day], key=f"admin_{member}_{day}")
            if st.button(f"Update {member_names[member] or member} - {day}", key=f"btn_{member}_{day}"):
                progress[member][day] = val
                save_progress(dict(progress))
                st.toast(f"✅ Updated {member_names[member] or member} - {day}", icon="✅")
    st.markdown('</div>', unsafe_allow_html=True)
    st.snow()
    # Confetti if all members have updated all days
    if all(all(progress[m][d].strip() for d in DAYS_OF_WEEK) for m in TEAM_MEMBERS):
        st.success("🎉 All members have updated their weekly progress!")
    # Team completion chart (number of members who updated all days)
    completed = sum(1 for m in TEAM_MEMBERS if all(progress[m][d].strip() for d in DAYS_OF_WEEK))
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = completed,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Members with Full Weekly Progress"},
        gauge = {
            'axis': {'range': [0, len(TEAM_MEMBERS)]},
            'bar': {'color': "#6a0572"},
            'steps' : [
                {'range': [0, len(TEAM_MEMBERS)//2], 'color': "#f5d6e6"},
                {'range': [len(TEAM_MEMBERS)//2, len(TEAM_MEMBERS)], 'color': "#c3cfe2"}
            ],
        }
    ))
    st.plotly_chart(fig, use_container_width=True)
# --- Block admin dashboard if not authenticated ---
elif name == ADMIN_USERNAME:
    st.warning("Please enter the correct admin password to view the dashboard.")
# --- Animated/Colorful Overview (for all users) ---
st.markdown("---")
st.markdown("## 🌟 Team Progress Overview (Current Day)")
today = datetime.datetime.now().strftime("%A")
member_names = st.session_state['member_names']
for member in TEAM_MEMBERS:
    prog = st.session_state['progress'][member].get(today, "")
    color = f"hsl({(TEAM_MEMBERS.index(member)*30)%360}, 80%, 80%)"
    st.markdown(f'<div style="background:{color};border-radius:0.5em;padding:0.5em 1em;margin-bottom:0.5em;"> <b>{member_names[member] or member}:</b> {prog or "<i>No update yet</i>"} </div>', unsafe_allow_html=True)
# Animated bar chart for team completion (today)
st.markdown("### Team Progress Completion (Today)")
bar_colors = ["#6a0572" if st.session_state['progress'][m].get(today, "").strip() else "#e0c3fc" for m in TEAM_MEMBERS]
bar_fig = go.Figure(go.Bar(
    x=[member_names[m] or m for m in TEAM_MEMBERS],
    y=[1 if st.session_state['progress'][m].get(today, "").strip() else 0 for m in TEAM_MEMBERS],
    marker_color=bar_colors,
    text=["Done" if st.session_state['progress'][m].get(today, "").strip() else "Pending" for m in TEAM_MEMBERS],
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
