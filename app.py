# Standard library imports
import os
import shutil
from datetime import datetime, timedelta
import io
import uuid

# Third-party imports
import streamlit as st
import pandas as pd
import pytz
import plotly.graph_objects as go
import plotly.express as px
import face_recognition
from PIL import Image 
import numpy as np

def is_face_already_registered(new_face_encoding, reg_student_id):
    faces_dir = "registered_faces"
    for fname in os.listdir(faces_dir):
        if fname.endswith(".jpg") and not fname.startswith(reg_student_id):
            img_path = os.path.join(faces_dir, fname)
            img = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(img)
            if encodings and face_recognition.compare_faces([encodings[0]], new_face_encoding, tolerance=0.5)[0]:
                return fname.split("_")[0]
    return None

# ---------- Page config ----------
st.set_page_config(
    page_title="🎓 Face Attendance Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* Global reset for consistency */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

/* Main background with subtle 3D effect */
.main, [data-testid="stAppViewContainer"] {
    background: linear-gradient(145deg, #f0f2f5 0%, #e0e7ff 100%);
    padding: 20px;
    min-height: 100vh;
}

/* Stylish tab bar with 3D effect */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1), inset 0 -2px 4px rgba(0, 0, 0, 0.05);
    gap: 16px;
}

/* Tab buttons with embossed look */
.stTabs [data-baseweb="tab"] {
    background: #e0e7ff;
    border-radius: 10px;
    color: #1e3a8a;
    font-weight: 600;
    padding: 12px 24px;
    transition: all 0.3s ease;
}
.stTabs [aria-selected="true"] {
    background: #3b82f6;
    color: white;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
}

/* Button styling with 3D hover effect */
.stButton > button {
    background: linear-gradient(90deg, #3b82f6, #60a5fa);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.8rem 2.5rem;
    font-weight: 600;
    font-size: 16px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15), inset 0 2px 4px rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

/* Card styling with 3D depth */
.custom-card {
    background: #ffffff;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid #e5e7eb;
    margin-bottom: 24px;
    transition: transform 0.3s ease;
}
.custom-card:hover {
    transform: translateY(-4px);
}

/* Metric circles with 3D effect */
.metric-card {
    background: linear-gradient(135deg, #3b82f6, #1e3a8a);
    color: white;
    padding: 1.5rem;
    border-radius: 50%;
    text-align: center;
    margin: 16px auto;
    min-width: 120px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2), inset 0 2px 4px rgba(255, 255, 255, 0.2);
    font-size: 1.1rem;
    transition: transform 0.3s ease;
}
.metric-card:hover {
    transform: scale(1.05);
}

/* Main header with layered shadow */
.main-header {
    background: linear-gradient(135deg, #3b82f6, #1e40af);
    padding: 3rem;
    border-radius: 20px;
    text-align: center;
    color: white;
    margin-bottom: 2.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2), inset 0 2px 4px rgba(255, 255, 255, 0.1);
}

/* Typography for clarity and professionalism */
body, .css-1d391kg, .stText, .stMarkdown {
    color: #1f2937 !important;
    font-family: 'Inter', sans-serif;
}
h1, h2, h3, h4, h5, h6 {
    color: #111827 !important;
    font-family: 'Inter', sans-serif;
    font-weight: 700;
}

/* Ensure button text is dark for visibility */
button[class*="stButton"] {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("""
    <div style="background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
                min-height: 400px; border-radius: 24px; margin-bottom: 2.5rem; padding: 60px 40px 30px 40px;
                text-align: center; box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2), inset 0 2px 4px rgba(255, 255, 255, 0.1);">
        <div style="margin-bottom: 32px;">
            <span style="background: white; border-radius: 50%; display: inline-block; padding: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);">
                <svg height="56" width="56"><circle cx="28" cy="28" r="26" fill="#3b82f6"/><text x="27" y="38" font-size="32" text-anchor="middle" fill="white">🎓</text></svg>
            </span>
        </div>
        <h1 style="font-size: 3.5rem; font-weight: 800; color: white; margin-bottom: 16px; letter-spacing: -1.5px;">
            Face Attendance System
        </h1>
        <div style="font-size: 1.4rem; color: #e0e7ff; margin-bottom: 24px; line-height: 1.5;">
            Secure, modern, and efficient biometric attendance tracking for educational institutions
        </div>
        <a href="#get-started-anchor">
            <button style="background: white; color: #1e40af; font-weight: 600; font-size: 1.2rem;
                           padding: 14px 48px; border-radius: 14px; margin: 12px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
                           border: none; transition: all 0.3s ease;">
                Get Started
            </button>
        </a>
    </div>
""", unsafe_allow_html=True)

# --- Feature Boxes ---
st.markdown('<div id="get-started-anchor"></div>', unsafe_allow_html=True)
features = [
    {"icon": "📷", "title": "Face Recognition", "desc": "Advanced biometric verification using AI-powered face detection"},
    {"icon": "📊", "title": "Real-time Analytics", "desc": "Track attendance trends and performance metrics instantly"},
    {"icon": "🔒", "title": "Secure & Private", "desc": "Enterprise-grade security with encrypted data storage"},
    {"icon": "⏰", "title": "Morning & Evening", "desc": "Dual session attendance tracking with late detection"},
]
cols = st.columns(len(features))
for i, feat in enumerate(features):
    cols[i].markdown(f"""
        <div style='background: #ffffff; border-radius: 16px; padding: 24px 20px; margin-bottom: 16px;
                     box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), inset 0 2px 4px rgba(255, 255, 255, 0.1);
                     min-height: 180px; transition: transform 0.3s ease;'>
            <div style='font-size: 3rem; margin-bottom: 16px; text-align: center; color: #3b82f6;'>{feat['icon']}</div>
            <div style='font-size: 1.3rem; font-weight: 600; color: #111827; margin-bottom: 12px; text-align: center;'>{feat['title']}</div>
            <div style='font-size: 1rem; color: #4b5563; line-height: 1.5; text-align: center;'>{feat['desc']}</div>
        </div>
    """, unsafe_allow_html=True)

IMAGE_FOLDER = "captured_images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs("registered_faces", exist_ok=True)
period_columns = [f"Period{i}" for i in range(1, 9)]
columns = ["StudentID", "Name", "Date", "Time", "Image", "Morning", "Evening",
           "Attendance%", "LateMorning", "LateEvening", "AbsentReason"] + period_columns
ATTENDANCE_FILE = "attendance_records.csv"

if not os.path.exists(ATTENDANCE_FILE):
    df = pd.DataFrame(columns=columns)
    df.to_csv(ATTENDANCE_FILE, index=False)
else:
    df = pd.read_csv(ATTENDANCE_FILE)
    for col in columns:
        if col not in df.columns:
            df[col] = "Absent" if col in period_columns else ""
    df = df[columns]

STUDENTS = [{"id": f"S{str(i).zfill(3)}", "name": name} for i, name in enumerate([
    "Alice Johnson", "Bob Smith", "Charlie Lee", "Diana Patel", "Edward Kim", "Fiona Zhang",
    "George Lopez", "Hannah Green", "Isaac Perez", "Julia Singh", "Kevin Brown", "Laura Wilson",
    "Mathew White", "Nina Carter", "Oscar Hernandez", "Priya Gupta", "Quentin Rogers", "Rachel Evans",
    "Samuel Miller", "Tina Anderson", "Uma Reddy", "Victor Garcia", "Wendy Thomas", "Xander Reed",
    "Yara Clark", "Zachary Turner", "Adam Nelson", "Bethany Scott", "Cyrus Bell", "Devika Nair",
    "Elijah Wolf", "Fatima Khan", "Gavin Rice", "Hailey Brooks", "Ian Kelly", "Jasmine Moore",
    "Karthik Sharma", "Leah Stewart", "Maya Foster", "Noah Russell", "Olivia Hayes", "Puneet Jain",
    "Riya Mehta", "Sahil Singh", "Tanvi Joshi", "Umar Ahmad", "Varsha Aggarwal", "Waleed Hussain",
    "Xin Wei", "Yusuf Ali"], start=1)]

# Simple parent-child mapping (for demo purposes)
PARENT_MAPPING = {
    f"P{str(i).zfill(3)}": s["id"] for i, s in enumerate(STUDENTS, start=1)
}

def get_ist_now():
    return datetime.now(pytz.timezone("Asia/Kolkata"))

def profile_completion():
    completeness = 0
    if st.session_state.get("student_name"):
        completeness += 40
    if st.session_state.get("student_id"):
        completeness += 40
    completeness += 20
    return completeness

def generate_summary_report(student_df):
    if student_df.empty:
        return None
    buffer = io.StringIO()
    summary = student_df.groupby('Date')[['Morning', 'Evening']].apply(
        lambda x: (x == "Present").sum()).reset_index()
    summary['Date'] = pd.to_datetime(summary['Date']).dt.strftime('%Y-%m-%d')
    summary.to_csv(buffer, index=False)
    return buffer.getvalue().encode('utf-8')

def attendance_correction_request():
    st.subheader("Attendance Correction Request")
    date_req = st.date_input("Date of Attendance to Correct")
    session_req = st.selectbox("Session", ["Morning", "Evening"])
    reason_req = st.text_area("Reason for Correction (explain clearly)")
    img_req = st.file_uploader("Upload Proof Image (Optional)", type=['png', 'jpg', 'jpeg'])
    if st.button("Submit Correction Request"):
        with open('correction_requests.txt', 'a') as f:
            request_id = str(uuid.uuid4())
            line = f"{request_id},{st.session_state.student_id},{st.session_state.student_name},{date_req},{session_req},{reason_req}\n"
            f.write(line)
        st.success("Correction request submitted! Admin will review it soon.")

def load_all_registered_encodings():
    encodings = []
    for fname in os.listdir("registered_faces"):
        if fname.endswith(".jpg"):
            path = os.path.join("registered_faces", fname)
            image = face_recognition.load_image_file(path)
            e = face_recognition.face_encodings(image)
            if e:
                encodings.append((fname, e[0]))
    return encodings

def load_registered_encodings(student_id):
    encodings = []
    for fname in os.listdir("registered_faces"):
        if fname.startswith(f"{student_id}_") and fname.endswith(".jpg"):
            img_path = os.path.join("registered_faces", fname)
            image = face_recognition.load_image_file(img_path)
            e = face_recognition.face_encodings(image)
            if e:
                encodings.append(e[0])
    return encodings

def verify_face_multiple(live_image_file, registered_encodings, tolerance=0.5):
    live_image = Image.open(live_image_file)
    live_image_np = np.array(live_image)
    live_encodings = face_recognition.face_encodings(live_image_np)
    if not live_encodings:
        return False, "No face detected in live image."
    live_encoding = live_encodings[0]
    for reg_encoding in registered_encodings:
        if face_recognition.compare_faces([reg_encoding], live_encoding, tolerance=tolerance)[0]:
            return True, None
    return False, None

def mark_attendance(student_id, name, session, img_file, allow_increase=True):
    global df
    now = get_ist_now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    weekday = now.weekday()
    hour = now.hour

    allowed_morning = 7 <= hour < 9
    allowed_evening = 15 <= hour < 16

    if session == "Morning" and not allowed_morning:
        st.warning("Attendance allowed only between 7:00 and 9:00 AM for morning.")
        return
    if session == "Evening" and not allowed_evening:
        st.warning("Attendance allowed only between 3:00 and 4:00 PM for evening.")
        return

    registered_encodings = load_registered_encodings(student_id)
    if not registered_encodings:
        st.error("No registered face found for this ID. Please register first!")
        return

    face_match, face_err = verify_face_multiple(img_file, registered_encodings)
    if face_err:
        st.error(face_err)
        return
    if not face_match:
        st.warning("Face does not match registered student. Attendance denied.")
        return

    live_image = Image.open(img_file)
    live_image_np = np.array(live_image)
    live_encodings = face_recognition.face_encodings(live_image_np)
    if not live_encodings:
        st.error("No face detected in the attendance capture.")
        return
    live_encoding = live_encodings[0]

    other_students_mask = (df['Date'] == date_str) & (df['StudentID'] != student_id)
    other_records = df[other_students_mask]
    tolerance = 0.5
    for _, row in other_records.iterrows():
        img_path = row['Image']
        if img_path and os.path.exists(img_path):
            try:
                img_reg = face_recognition.load_image_file(img_path)
                encodings_reg = face_recognition.face_encodings(img_reg)
                if encodings_reg:
                    if face_recognition.compare_faces([encodings_reg[0]], live_encoding, tolerance=tolerance)[0]:
                        st.error("This face is already used for another student today.")
                        return
            except Exception as e:
                st.error(f"Error processing image for face comparison: {e}")
                return

    todays_attendance = df[(df['StudentID'] == student_id) & (df['Date'] == date_str)]
    if not todays_attendance.empty:
        row = todays_attendance.iloc[0]
        morning_attended = row['Morning'] == 'Present'
        evening_attended = row['Evening'] == 'Present'
        if session == "Morning" and morning_attended:
            st.info("You have already marked morning attendance today.")
            return
        if session == "Evening" and evening_attended:
            st.info("You have already marked evening attendance today.")
            return
        if morning_attended and evening_attended:
            st.warning("You have already marked morning and evening attendance today.")
            return

    if todays_attendance.empty:
        new_row = pd.DataFrame([[student_id, name, date_str, time_str, "", "None", "None", 0, "", "", "Absent"] + ["Absent"] * 8], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        idx = df.index[-1]
    else:
        idx = todays_attendance.index[0]
    timestamp = now.strftime("%Y%m%d%H%M%S")
    img_path = os.path.join(IMAGE_FOLDER, f"{name}_{timestamp}.png")
    with open(img_path, "wb") as f:
        f.write(img_file.getbuffer())
    df.at[idx, "Image"] = img_path
    df.at[idx, session] = "Present"

    if session == "Morning":
        df.at[idx, "LateMorning"] = "" if allowed_morning else "Late"
    elif session == "Evening":
        df.at[idx, "LateEvening"] = "" if allowed_evening else "Late"

    if allow_increase and weekday != 6:
        morning = df.at[idx, "Morning"] == "Present"
        evening = df.at[idx, "Evening"] == "Present"
        if morning and evening:
            df.at[idx, "Attendance%"] = min(100, df.at[idx, "Attendance%"] + 1)

    st.success(f"{session} attendance recorded successfully!")
    df.to_csv(ATTENDANCE_FILE, index=False)

def mark_period_attendance(student_id, name, date_str, period, status="Present"):
    global df
    mask = (df["StudentID"] == student_id) & (df["Date"] == date_str)
    filtered = df[mask]
    if not filtered.empty:
        idx = filtered.index[0]
    else:
        now = get_ist_now()
        time_str = now.strftime("%H:%M:%S")
        new_row = pd.DataFrame([[student_id, name, date_str, time_str, "",
                                "None", "None", 0, "", "", "Absent"] + ["Absent"] * 8], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        idx = df.index[-1]
    df.at[idx, period] = status
    df.to_csv(ATTENDANCE_FILE, index=False)

def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.session_state["refresh_app"] = True

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "student_id" not in st.session_state:
    st.session_state.student_id = ""
if "parent_child_id" not in st.session_state:
    st.session_state.parent_child_id = ""
if "refresh_app" not in st.session_state:
    st.session_state["refresh_app"] = False

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.student_name = ""
    st.session_state.student_id = ""
    st.session_state.parent_child_id = ""
    safe_rerun()

if st.session_state.get("refresh_app", False):
    st.session_state["refresh_app"] = False
    try:
        st.rerun()
    except AttributeError:
        pass

FACULTY_SECRET_KEY = "Faculty2025Secret!"
ADMIN_SECRET_KEY = "Admin2025Secret!"

if not st.session_state.logged_in:
    st.markdown("""
        <div class="login-container">
            <div class="login-title">🎓 Welcome to Face Attendance System</div>
            <div class="sub-title">Smart • Secure • Simple</div>
        </div>
        """, unsafe_allow_html=True)

    login_option = st.selectbox("Login as:", ["Student", "Faculty", "Parent", "Admin"], key="login_role")
    if login_option == "Student":
        name_input = st.text_input("Enter your Name", key="student_name_login")
        id_input = st.text_input("Enter your Student ID", key="student_id_login")
        if st.button("Login as Student"):
            if name_input and id_input:
                st.session_state.logged_in = True
                st.session_state.user_role = "student"
                st.session_state.student_name = name_input.strip()
                st.session_state.student_id = id_input.strip()
                safe_rerun()
            else:
                st.warning("Please enter both name and student ID.")
    elif login_option == "Faculty":
        secret_key_input = st.text_input("Enter Faculty Secret Key", type="password", key="faculty_secret")
        faculty_name_input = st.text_input("Enter Your Name", key="faculty_name")
        if st.button("Login as Faculty"):
            if secret_key_input == FACULTY_SECRET_KEY and faculty_name_input:
                st.session_state.logged_in = True
                st.session_state.user_role = "faculty"
                st.session_state.student_name = faculty_name_input.strip()
                st.session_state.student_id = "FACULTY"
                safe_rerun()
            else:
                st.warning("Invalid secret key or missing name")
    elif login_option == "Parent":
        parent_name = st.text_input("Enter Your Name", key="parent_name")
        child_name = st.selectbox("Select Your Child's Name", [s["name"] for s in STUDENTS], key="child_name")
        if st.button("Login as Parent"):
            if parent_name and child_name:
                child_id = next(s["id"] for s in STUDENTS if s["name"] == child_name)
                if child_id in [v for v in PARENT_MAPPING.values()]:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "parent"
                    st.session_state.student_name = parent_name.strip()
                    st.session_state.student_id = "PARENT"
                    st.session_state.parent_child_id = child_id
                    safe_rerun()
                else:
                    st.warning("Invalid child selection.")
            else:
                st.warning("Please enter your name and select your child's name.")
    else:  # Admin
        secret_key_input = st.text_input("Enter Admin Secret Key", type="password", key="admin_secret")
        admin_name_input = st.text_input("Enter Your Name", key="admin_name")
        if st.button("Login as Admin"):
            if secret_key_input == ADMIN_SECRET_KEY and admin_name_input:
                st.session_state.logged_in = True
                st.session_state.user_role = "admin"
                st.session_state.student_name = admin_name_input.strip()
                st.session_state.student_id = "ADMIN"
                safe_rerun()
            else:
                st.warning("Invalid secret key or missing name")
else:
    if st.session_state.user_role == "faculty":
        title_text = "🎓 Faculty Dashboard"
        tabs = st.tabs(["Register", "View Records", "Analytics", "My Profile", "My Images", 
                        "Leaderboard", "Timeline", "Correction Request", "Reports", 
                        "Period Attendance", "Period Analytics"])
        tab_reg, tab_view, tab_analytics, tab_profile, tab_images, tab_leaderboard, tab_timeline, tab_correction, tab_summary, tab_period, tab_period_analytics = tabs
    elif st.session_state.user_role == "parent":
        title_text = "🎓 Parent Portal"
        tabs = st.tabs(["View Records", "Analytics", "Timeline", "Reports"])
        tab_view, tab_analytics, tab_timeline, tab_summary = tabs
        student_id = st.session_state.parent_child_id
        student_name = next(s["name"] for s in STUDENTS if s["id"] == student_id)
    elif st.session_state.user_role == "admin":
        title_text = "🎓 Admin Dashboard"
        tabs = st.tabs(["Admin Dashboard", "View Records", "Analytics", "Timeline", "Reports"])
        tab_admin, tab_view, tab_analytics, tab_timeline, tab_summary = tabs
    else:
        title_text = "🎓 Student Portal"
        tabs = st.tabs(["Register", "View Records", "Analytics", "My Profile", "My Images", 
                        "Leaderboard", "Timeline", "Correction Request", "Reports", 
                        "Period Attendance", "Period Analytics"])
        tab_reg, tab_view, tab_analytics, tab_profile, tab_images, tab_leaderboard, tab_timeline, tab_correction, tab_summary, tab_period, tab_period_analytics = tabs
    st.markdown(f"<div class='main-header'><h1>{title_text}</h1></div>", unsafe_allow_html=True)

    if st.session_state.user_role != "parent" and st.session_state.user_role != "admin":
        with tab_reg:
            reg_student_id = st.text_input("Enter ID to Register", value=st.session_state.student_id)
            reg_student_name = st.text_input("Enter Name to Register", value=st.session_state.student_name)
            image_uploaded = st.camera_input("Capture registration image")

            reg_path = f"registered_faces/{reg_student_id}_1.jpg"
            os.makedirs("registered_faces", exist_ok=True)

            registration_success = False
            if image_uploaded is not None:
                new_face_image = Image.open(image_uploaded)
                new_face_encoding_list = face_recognition.face_encodings(np.array(new_face_image))
                if new_face_encoding_list:
                    new_face_encoding = new_face_encoding_list[0]
                    conflict_id = is_face_already_registered(new_face_encoding, reg_student_id)
                    if conflict_id:
                        st.error(f"This face is already registered to ID {conflict_id}. Each face can only be linked to one ID per semester. Please contact admin if this is an error.")
                    elif os.path.exists(reg_path):
                        st.error(f"Face and ID already registered for {reg_student_id}. Please contact admin to reset if you need to re-register.")
                    else:
                        with open(reg_path, "wb") as f:
                            f.write(image_uploaded.getbuffer())
                        st.success(f"Registration complete! Your face is now locked to ID {reg_student_id}. Only you can mark attendance for this ID.")
                        registration_success = True
                else:
                    st.warning("No face detected in this capture. Please try again.")
            else:
                st.info("Please capture your registration image.")

            now = get_ist_now()
            hour = now.hour
            allowed_morning = 7 <= hour < 9
            allowed_evening = 15 <= hour < 16

            def already_marked(session):
                todays_attendance = df[(df['StudentID'] == reg_student_id) & (df['Date'] == now.strftime("%Y-%m-%d"))]
                if not todays_attendance.empty:
                    row = todays_attendance.iloc[0]
                    return row[session] == 'Present'
                return False

            st.markdown("""
            <div style="margin-top:2rem;margin-bottom:2rem;">
                <h3 style="background: linear-gradient(90deg, #67e8f9, #764ba2); color:white; padding:8px 32px; border-radius:12px; display:inline-block; box-shadow:0 2px 8px rgba(100,100,150,0.10);">Mark Your Attendance</h3>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("""
                <style>
                    div.stButton > button:first-child {
                        background: linear-gradient(90deg, #1fa2ff, #12d8fa, #a6ffcb);
                        color: #222; font-weight: 600; font-size: 18px; border-radius: 18px;
                        height:48px; margin-bottom:20px; box-shadow: 0 4px 15px rgba(31,162,255,0.12);
                    }
                </style>
                """, unsafe_allow_html=True)
                if st.button("🌅 Morning Attendance"):
                    if not allowed_morning:
                        st.warning("Accessible only between 7:00 AM and 9:00 AM.")
                    elif already_marked("Morning"):
                        st.info("You have already marked morning attendance today.")
                    else:
                        registered_encodings = load_registered_encodings(reg_student_id)
                        if not registered_encodings:
                            st.error("No registered face found for this ID. Please register first!")
                        else:
                            match, _ = verify_face_multiple(image_uploaded, registered_encodings)
                            if not match:
                                st.warning("Face does not match registered student. Attendance denied.")
                            else:
                                mark_attendance(reg_student_id, reg_student_name, "Morning", image_uploaded)

            with col2:
                st.markdown("""
                <style>
                    div.stButton > button:nth-child(1) {
                        background: linear-gradient(90deg, #f7971e, #ffd200, #f7971e);
                        color: #222; font-weight: 600; font-size: 18px; border-radius: 18px;
                        height:48px; margin-bottom:20px; box-shadow: 0 4px 15px rgba(255,216,0,0.12);
                    }
                </style>
                """, unsafe_allow_html=True)
                if st.button("🌇 Evening Attendance"):
                    if not allowed_evening:
                        st.warning("Accessible only between 3:00 PM and 4:00 PM.")
                    elif already_marked("Evening"):
                        st.info("You have already marked evening attendance today.")
                    else:
                        registered_encodings = load_registered_encodings(reg_student_id)
                        if not registered_encodings:
                            st.error("No registered face found for this ID. Please register first!")
                        else:
                            match, _ = verify_face_multiple(image_uploaded, registered_encodings)
                            if not match:
                                st.warning("Face does not match registered student. Attendance denied.")
                            else:
                                mark_attendance(reg_student_id, reg_student_name, "Evening", image_uploaded)

    with tab_view:
        st.markdown("""
        <div class="custom-card">
            <h2>📋 Attendance Records</h2>
            <p>View and filter attendance history</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("📅 Start Date", value=get_ist_now())
        with col2:
            end_date = st.date_input("📅 End Date", value=get_ist_now())

        if st.session_state.user_role == "parent":
            filtered_df = df[(df['StudentID'] == student_id) & (df['Date'] >= str(start_date)) & (df['Date'] <= str(end_date))]
        else:
            filtered_df = df[(df['Date'] >= str(start_date)) & (df['Date'] <= str(end_date))]

        def highlight_absent(val):
            if val in ["None", "Absent"]:
                return 'background-color: #FFE6E6'
            elif val == "Present":
                return 'background-color: #E6FFE6'
            return ''

        st.dataframe(filtered_df.style.map(highlight_absent, subset=['Morning', 'Evening'] + period_columns), use_container_width=True)

        if st.session_state.user_role == "parent":
            student_df = filtered_df
        else:
            student_df = filtered_df[filtered_df['Name'] == st.session_state.student_name]

        if not student_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3>📊 Total Days</h3>
                    <h2>{}</h2>
                </div>
                """.format(student_df.shape[0]), unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h3>🌅 Morning</h3>
                    <h2>{}</h2>
                </div>
                """.format((student_df['Morning'] == 'Present').sum()), unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <h3>🌇 Evening</h3>
                    <h2>{}</h2>
                </div>
                """.format((student_df['Evening'] == 'Present').sum()), unsafe_allow_html=True)
            with col4:
                st.markdown("""
                <div class="metric-card">
                    <h3>📈 Average</h3>
                    <h2>{:.1f}%</h2>
                </div>
                """.format(student_df['Attendance%'].mean()), unsafe_allow_html=True)

            csv = student_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "💾 Download Attendance CSV",
                data=csv,
                file_name=f"{st.session_state.get('student_name', 'Student')}_attendance.csv",
                mime='text/csv',
                use_container_width=True
            )

    with tab_analytics:
        st.markdown("""
        <div class="custom-card">
            <h2>📊 Attendance Analytics</h2>
            <p>Visualize attendance patterns and trends</p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.user_role == "parent":
            student_df = df[df['StudentID'] == student_id]
        else:
            student_df = df[df['Name'] == st.session_state.student_name]

        if not student_df.empty:
            attendance_percent = student_df['Attendance%'].iloc[-1]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=student_df['Date'], y=student_df['Attendance%'],
                mode='lines+markers',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8, color='#764ba2'),
                name='Attendance %',
                fill='tonexty',
                fillcolor='rgba(102, 126, 234, 0.1)'
            ))
            fig.add_hline(y=75, line_dash="dash", line_color="#FF6B6B",
                          annotation_text="Minimum Required", annotation_position="top right")
            fig.update_layout(
                title="Attendance Trend",
                xaxis_title="Date",
                yaxis_title="Attendance %",
                template="plotly_white",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

            if attendance_percent < 75:
                st.markdown("""
                <div style='background: linear-gradient(90deg, #FF6B6B, #FF8E53); color: white; 
                padding: 1rem; border-radius: 10px; text-align: center; margin: 20px 0;'>
                    <h3>⚠️ Attendance Alert!</h3>
                    <p>Attendance is {}%. Improvement needed to reach 75%</p>
                </div>
                """.format(attendance_percent), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background: linear-gradient(90deg, #56ab2f, #a8e6cf); color: white; 
                padding: 1rem; border-radius: 10px; text-align: center; margin: 20px 0;'>
                    <h3>🎉 Great Job!</h3>
                    <p>Attendance is {}%. Keep it up!</p>
                </div>
                """.format(attendance_percent), unsafe_allow_html=True)

            heat_df = student_df[['Date', 'Morning', 'Evening']].melt(id_vars='Date', var_name='Session', value_name='Status')
            heat_df['Status_Num'] = heat_df['Status'].apply(lambda x: 1 if x == 'Present' else 0)
            fig2 = px.density_heatmap(heat_df, x='Date', y='Session', z='Status_Num',
                                     color_continuous_scale=['#FFE6E6', '#667eea'],
                                     title="Attendance Heatmap")
            st.plotly_chart(fig2, use_container_width=True)

    if st.session_state.user_role not in ["parent", "admin"]:
        with tab_profile:
            st.markdown(f"""
            <div class="custom-card">
                <h2>👤 {st.session_state.student_name}'s Profile</h2>
                <p>Your personal dashboard and achievements</p>
            </div>
            """, unsafe_allow_html=True)

            comp_pct = profile_completion()
            st.markdown("### 📊 Profile Completion")
            st.progress(comp_pct / 100)
            st.write(f"**{comp_pct}% Complete**")

            student_df = df[df['Name'] == st.session_state.student_name]
            if not student_df.empty:
                latest = student_df.iloc[-1]
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🌅 Morning Status", latest["Morning"])
                with col2:
                    st.metric("🌇 Evening Status", latest["Evening"])
                with col3:
                    st.metric("📈 Attendance %", f"{latest['Attendance%']}%")

                st.markdown("### 🏆 Achievement Badges")
                if latest['Attendance%'] >= 95:
                    st.markdown("""
                    <div style='background: linear-gradient(45deg, #FFD700, #FFA500); padding: 15px; 
                    border-radius: 10px; text-align: center; margin: 10px;'>
                        <h3>🥇 Platinum Badge</h3>
                        <p>Outstanding Attendance (95%+)</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                elif latest['Attendance%'] >= 90:
                    st.markdown("""
                    <div style='background: linear-gradient(45deg, #C0C0C0, #A9A9A9); padding: 15px; 
                    border-radius: 10px; text-align: center; margin: 10px;'>
                        <h3>🥈 Gold Badge</h3>
                        <p>Excellent Attendance (90%+)</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif latest['Attendance%'] >= 75:
                    st.markdown("""
                    <div style='background: linear-gradient(45deg, #CD7F32, #B87333); padding: 15px; 
                    border-radius: 10px; text-align: center; margin: 10px;'>
                        <h3>🥉 Bronze Badge</h3>
                        <p>Good Attendance (75%+)</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style='background: linear-gradient(45deg, #FF6B6B, #FF8E53); padding: 15px; 
                    border-radius: 10px; text-align: center; margin: 10px;'>
                        <h3>💪 Improvement Needed</h3>
                        <p>Work harder to earn your first badge!</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No attendance data available yet. Start marking your attendance!")

        with tab_images:
            st.markdown("""
            <div class="custom-card">
                <h2>📸 My Attendance Images</h2>
                <p>Gallery of your captured attendance photos</p>
            </div>
            """, unsafe_allow_html=True)

            student_images = [f for f in os.listdir(IMAGE_FOLDER) if f.startswith(st.session_state.student_name)]
            student_images.sort(reverse=True)

            if student_images:
                cols = st.columns(4)
                for idx, img_file in enumerate(student_images):
                    img_path = os.path.join(IMAGE_FOLDER, img_file)
                    with cols[idx % 4]:
                        st.image(img_path, caption=os.path.basename(img_file), width=150)
            else:
                st.info("No attendance images found yet!")

        with tab_leaderboard:
            st.markdown("""
            <div class="custom-card">
                <h2>🏆 Attendance Leaderboard</h2>
                <p>See how you rank among all students</p>
            </div>
            """, unsafe_allow_html=True)

            leaderboard_df = df.groupby('Name')['Attendance%'].max().reset_index()
            leaderboard_df['Attendance%'] = pd.to_numeric(leaderboard_df['Attendance%'], errors='coerce')
            leaderboard_df = leaderboard_df[leaderboard_df['Attendance%'] > 0].sort_values('Attendance%', ascending=False)
            leaderboard_df['Rank'] = range(1, len(leaderboard_df) + 1)
            leaderboard_df['Medal'] = leaderboard_df['Rank'].apply(
                lambda x: "🥇" if x == 1 else "🥈" if x == 2 else "🥉" if x == 3 else "⭐"
            )

            st.dataframe(
                leaderboard_df[['Medal', 'Rank', 'Name', 'Attendance%']].style.highlight_max('Attendance%', color='lightgreen'),
                use_container_width=True
            )

            if not leaderboard_df.empty:
                top_student = leaderboard_df.iloc[0]
                st.markdown(f"""
                <div style='background: linear-gradient(45deg, #FFD700, #FFA500); padding: 20px; 
                border-radius: 15px; text-align: center; margin: 20px 0;'>
                    <h2>👑 Top Performer</h2>
                    <h3>{top_student['Name']}</h3>
                    <p>{top_student['Attendance%']}% Attendance</p>
                </div>
                """, unsafe_allow_html=True)

    with tab_timeline:
        st.markdown("""
        <div class="custom-card">
            <h2>⏳ Attendance Timeline</h2>
            <p>Visual timeline of attendance history</p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.user_role == "parent":
            student_df = df[df['StudentID'] == student_id]
        else:
            student_df = df[df['Name'] == st.session_state.student_name]

        if not student_df.empty:
            timeline_df = student_df[['Date', 'Morning', 'Evening']].copy()
            timeline_df['color'] = timeline_df.apply(
                lambda row: '#56ab2f' if row['Morning'] == 'Present' and row['Evening'] == 'Present'
                else '#FFD93D' if row['Morning'] == 'Present' or row['Evening'] == 'Present'
                else '#FF6B6B', axis=1
            )
            timeline_df['Status'] = timeline_df.apply(
                lambda row: 'Full Day' if row['Morning'] == 'Present' and row['Evening'] == 'Present'
                else 'Partial' if row['Morning'] == 'Present' or row['Evening'] == 'Present'
                else 'Absent', axis=1
            )

            fig = go.Figure(data=[go.Scatter(
                x=timeline_df['Date'],
                y=[1] * len(timeline_df),
                mode='markers',
                marker=dict(color=timeline_df['color'], size=20),
                text=timeline_df['Status'],
                hovertemplate='<b>Date:</b> %{x}<br><b>Status:</b> %{text}<extra></extra>',
                name='Attendance Timeline'
            )])
            fig.update_layout(
                yaxis_visible=False,
                title="Attendance Timeline",
                height=300,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("🟢 **Full Day** - Morning + Evening")
            with col2:
                st.markdown("🟡 **Partial** - Morning OR Evening")
            with col3:
                st.markdown("🔴 **Absent** - No attendance")
        else:
            st.info("No attendance data to display timeline!")

    if st.session_state.user_role not in ["parent", "admin"]:
        with tab_correction:
            attendance_correction_request()

    with tab_summary:
        st.markdown("""
        <div class="custom-card">
            <h2>📥 Download Reports</h2>
            <p>Generate and download attendance summaries</p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.user_role == "parent":
            student_df = df[df['StudentID'] == student_id]
        else:
            student_df = df[df['Name'] == st.session_state.student_name]

        data_bytes = generate_summary_report(student_df)

        if data_bytes:
            st.download_button(
                label="📥 Download Attendance Summary",
                data=data_bytes,
                file_name=f"{st.session_state.get('student_name', 'Student')}_attendance_summary.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No data available to generate report.")

    if st.session_state.user_role not in ["parent", "admin"]:
        with tab_period:
            st.markdown("""
            <div class="custom-card">
                <h2>🕐 Period-wise Attendance</h2>
                <p>Track attendance for individual class periods</p>
            </div>
            """, unsafe_allow_html=True)

            selected_date = st.date_input("Select Date", value=get_ist_now().date())
            weekday = selected_date.weekday()
            period_columns = [f"Period{i}" for i in range(1, 9)]

            if weekday > 5:
                st.warning("Selected day is a weekend - no classes scheduled.")
            else:
                st.markdown(f"### 📅 Attendance for {selected_date.strftime('%A, %B %d, %Y')}")

                if st.session_state.user_role == "faculty":
                    st.markdown("### 👨‍🏫 Faculty: Mark Period Attendance")

                    period_choice = st.selectbox("Select Period", period_columns, index=0)
                    key_prefix = f"period_{period_choice}_{selected_date}"

                    student_names = [s['name'] for s in STUDENTS]
                    if key_prefix not in st.session_state:
                        st.session_state[key_prefix] = {name: False for name in student_names}

                    cols = st.columns(5)
                    for idx, student in enumerate(STUDENTS):
                        name = student['name']
                        present = st.session_state[key_prefix][name]
                        button_style = (
                            "background-color: #FF4B4B; color: white; border-radius: 10px; font-weight: bold; border: none; font-size: 1.1rem; margin-bottom: 12px; height:50px;"
                            if not present else
                            "background-color: #45c490; color: white; border-radius: 10px; font-weight: bold; border: none; font-size: 1.1rem; margin-bottom: 12px; height:50px;"
                        )

                        if cols[idx % 5].button(f"{'✅ Present' if present else '❌ Absent'} {name}", key=f"{key_prefix}_{name}"):
                            st.session_state[key_prefix][name] = not present
                            st.rerun()

                    if st.button("Submit Period Attendance", use_container_width=True):
                        for student in STUDENTS:
                            status = "Present" if st.session_state[key_prefix][student['name']] else "Absent"
                            mark_period_attendance(student['id'], student['name'], str(selected_date), period_choice, status)
                        st.success(f"{period_choice} attendance updated successfully!")
                else:
                    st.markdown("### 📊 Your Period Attendance")
                    mask = (df["StudentID"] == st.session_state.student_id) & (df["Date"] == str(selected_date))
                    filtered = df[mask]
                    if not filtered.empty:
                        rec = filtered.iloc[0]
                        present_periods = sum([rec[p] == "Present" for p in period_columns])
                        period_attendance_pct = present_periods * 12.5

                        color = "#56ab2f" if period_attendance_pct >= 75 else "#FF6B6B"

                        st.markdown(f"""
                        <h3>Overall Period Attendance:</h3>
                        <div style='width:100%;height:32px;position:relative;background:#eee;border-radius:20px;'>
                          <div style='width:{period_attendance_pct}%;height:100%;background:{color};border-radius:20px;transition:width 0.3s;'></div>
                          <div style='position:absolute;top:0;left:8px;height:100%;line-height:32px;font-weight:bold;color:#222;'>{period_attendance_pct:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)

                        cols = st.columns(8)
                        for i, p in enumerate(period_columns):
                            status = rec[p]
                            color_period = "#56ab2f" if status == "Present" else "#FF6B6B"
                            emoji = "✅" if status == "Present" else "❌"
                            cols[i].markdown(f"""
                                <div style='background: {color_period}; padding: 15px; border-radius: 10px; 
                                text-align: center; margin: 5px; color: white; font-weight: bold;'>
                                    <div>{emoji}</div>
                                    <div>{p}</div>
                                    <div>{status}</div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No period attendance data for selected date.")

        with tab_period_analytics:
            st.markdown("""
            <div class="custom-card">
                <h2>📈 Period-wise Analytics</h2>
                <p>Track your overall period attendance performance</p>
            </div>
            """, unsafe_allow_html=True)

            student_df = df[df['Name'] == st.session_state.student_name]
            if not student_df.empty:
                total_days = len(student_df)
                if total_days > 0:
                    total_slots = total_days * 8
                    total_present = sum((student_df[p] == "Present").sum() for p in period_columns)
                    total_absent = total_slots - total_present
                    total_score = total_present * 1 - total_absent * 0.3
                    overall_percent = max(0, min(100, (total_score / total_slots) * 100))

                    bar_color = "#56ab2f" if overall_percent >= 75 else "#FF6B6B"

                    st.markdown(f"""
                    <div style="margin: 20px 0;">
                        <h3>Overall Period Attendance:</h3>
                        <div style="width: 100%; height: 32px; position: relative; background: #eee; border-radius: 20px;">
                            <div style="width: {overall_percent}%; height: 100%; background: {bar_color}; border-radius: 20px; transition: width 0.3s;"></div>
                            <div style="position: absolute; top: 0; left: 8px; height: 100%; line-height: 32px; font-weight: bold; color: #222;">
                                {overall_percent:.2f}%
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No attendance data available yet.")
            else:
                st.info("No attendance data available yet.")

    if st.session_state.user_role == "admin":
        with tab_admin:
            st.markdown("""
            <div class="custom-card">
                <h2>🔧 Admin Dashboard</h2>
                <p>Manage student registrations, approve correction requests, and view system-wide analytics</p>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("🛠️ Manage Student Registrations")
            student_id_to_reset = st.selectbox("Select Student ID to Reset Face Data", [s["id"] for s in STUDENTS])
            if st.button("Reset Face Data"):
                reg_path = f"registered_faces/{student_id_to_reset}_1.jpg"
                if os.path.exists(reg_path):
                    os.remove(reg_path)
                    st.success(f"Face data for {student_id_to_reset} has been reset.")
                else:
                    st.warning("No face data found for this student.")

            st.subheader("✅ Approve Correction Requests")
            if os.path.exists("correction_requests.txt"):
                with open("correction_requests.txt", "r") as f:
                    requests = [line.strip().split(",") for line in f if line.strip()]
                if requests:
                    requests_df = pd.DataFrame(requests, columns=["RequestID", "StudentID", "Name", "Date", "Session", "Reason"])
                    st.dataframe(requests_df[["StudentID", "Name", "Date", "Session", "Reason"]], use_container_width=True)
                    request_id_to_approve = st.selectbox("Select Request ID to Approve", requests_df["RequestID"])
                    if st.button("Approve Correction"):
                        request = requests_df[requests_df["RequestID"] == request_id_to_approve].iloc[0]
                        mask = (df["StudentID"] == request["StudentID"]) & (df["Date"] == request["Date"])
                        if not df[mask].empty:
                            idx = df[mask].index[0]
                            df.at[idx, request["Session"]] = "Present"
                            df.to_csv(ATTENDANCE_FILE, index=False)
                            with open("correction_requests.txt", "r") as f:
                                lines = f.readlines()
                            with open("correction_requests.txt", "w") as f:
                                for line in lines:
                                    if not line.startswith(request_id_to_approve):
                                        f.write(line)
                            st.success(f"Correction approved for {request['Name']} on {request['Date']} for {request['Session']}.")
                        else:
                            st.error("No attendance record found for this request.")
                else:
                    st.info("No pending correction requests.")
            else:
                st.info("No pending correction requests.")

            st.subheader("📊 System-wide Analytics")
            total_students = len(df["StudentID"].unique())
            total_days = len(df["Date"].unique())
            avg_attendance = df["Attendance%"].mean()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>👥 Total Students</h3>
                    <h2>{total_students}</h2>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📅 Total Days</h3>
                    <h2>{total_days}</h2>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📈 Avg Attendance</h3>
                    <h2>{avg_attendance:.1f}%</h2>
                </div>
                """, unsafe_allow_html=True)

            fig = px.histogram(df, x="Attendance%", nbins=20, title="Distribution of Attendance %")
            st.plotly_chart(fig, use_container_width=True)

    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(180deg, #667eea, #764ba2); padding: 20px; 
        border-radius: 15px; text-align: center; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0;'>📢 Activity Feed</h2>
        </div>
        """, unsafe_allow_html=True)

        recent_logs = df.tail(5)
        for _, row in recent_logs.iterrows():
            st.info(f"**{row['Name']}**\n🌅 {row['Morning']} | 🌇 {row['Evening']}\n📅 {row['Date']}")

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🎓 Made with ❤️ using Streamlit | Face Attendance System v2.0</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get('show_welcome', True):
        st.toast(f"👋 Welcome {st.session_state.student_name}!", icon="🎉")
        st.session_state['show_welcome'] = False   

        
         
