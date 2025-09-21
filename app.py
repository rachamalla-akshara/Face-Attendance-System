import streamlit as st
import pandas as pd
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------- Config ----------
ATTENDANCE_FILE = "attendance_records.csv"
IMAGE_FOLDER = "captured_images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# ---------- Load or initialize CSV ----------
columns = ["Name", "Date", "Time", "Image"]
if not os.path.exists(ATTENDANCE_FILE):
    df = pd.DataFrame(columns=columns)
    df.to_csv(ATTENDANCE_FILE, index=False)
else:
    df = pd.read_csv(ATTENDANCE_FILE)
    # Keep only required columns to avoid column mismatch
    df = df[columns]

# ---------- Helper Functions ----------
def mark_attendance(name, image_path):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    global df
    # Prevent marking attendance twice on the same day
    if not ((df["Name"] == name) & (df["Date"] == date_str)).any():
        new_row = pd.DataFrame([[name, date_str, time_str, image_path]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(ATTENDANCE_FILE, index=False)
        st.success(f"✅ Attendance marked for {name} on {date_str} at {time_str}")
    else:
        st.warning(f"⚠️ Attendance already marked for {name} today.")

def send_email(sender_email, sender_password, student_email, name, status="Absent"):
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = student_email
        message["Subject"] = f"Attendance Notification - {status}"
        body = f"Hello {name},\n\nYou are marked {status} today.\n\n- Attendance System"
        message.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, student_email, message.as_string())
        st.success(f"🔔 Notification sent to {student_email}")
    except Exception as e:
        st.error(f"⚠️ Email could not be sent: {e}")

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Face Attendance Dashboard", layout="wide")

# ---------- Session State ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "student_id" not in st.session_state:
    st.session_state.student_id = ""

# ---------- Login Page ----------
if not st.session_state.logged_in:
    st.title("🎓 Student Login")
    name_input = st.text_input("Enter your Name")
    id_input = st.text_input("Enter your Student ID")
    if st.button("Login"):
        if name_input and id_input:
            st.session_state.logged_in = True
            st.session_state.student_name = name_input
            st.session_state.student_id = id_input
            st.success(f"Welcome {name_input}!")
        else:
            st.warning("Please fill in both fields.")

# ---------- Dashboard ----------
if st.session_state.logged_in:
    st.title(f"🎓 Welcome, {st.session_state.student_name}!")

    # --- Logout Button ---
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.student_name = ""
        st.session_state.student_id = ""
        st.experimental_rerun()  # Reload the app to show login page

    tab1, tab2, tab3 = st.tabs(["Mark Attendance", "View Records", "Send Absent Notification"])

    # --- Tab 1: Mark Attendance ---
    with tab1:
        st.header("📸 Mark Attendance")
        capture_method = st.radio("Select Method:", ["Upload Image", "Use Camera"], key="capture_method")

        if capture_method == "Upload Image":
            uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="upload_image")
            if uploaded_file:
                img_path = os.path.join(IMAGE_FOLDER, f"{st.session_state.student_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                mark_attendance(st.session_state.student_name, img_path)

        elif capture_method == "Use Camera":
            img_file_buffer = st.camera_input("Capture Image from Webcam")
            if img_file_buffer:
                img_path = os.path.join(IMAGE_FOLDER, f"{st.session_state.student_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
                with open(img_path, "wb") as f:
                    f.write(img_file_buffer.getbuffer())
                mark_attendance(st.session_state.student_name, img_path)

    # --- Tab 2: View Records ---
    with tab2:
        st.header("📊 Attendance Records")
        if not df.empty:
            st.dataframe(df)
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", data=csv_data, file_name="attendance_records.csv", mime="text/csv", key="download_csv")
        else:
            st.info("No attendance records yet.")

    # --- Tab 3: Send Absent Notification ---
    with tab3:
        st.header("🔔 Send Absent Notification")
        sender_email = st.text_input("Your Gmail Address", key="sender_email")
        sender_password = st.text_input("Your App Password", type="password", key="sender_password")
        absent_name = st.text_input("Student Name to Notify", key="absent_name")
        absent_email = st.text_input("Student Email", key="absent_email")

        if st.button("Send Notification", key="send_absent"):
            if sender_email and sender_password and absent_name and absent_email:
                send_email(sender_email, sender_password, absent_email, absent_name, status="Absent")
            else:
                st.warning("Fill all fields (your email, password, student name, student email)")

    # --- Optional Analytics ---
    with st.expander("📈 Attendance Analytics"):
        st.subheader("Attendance Trend")
        if not df.empty:
            chart_data = df.groupby("Date").size().reset_index(name="Count")
            st.bar_chart(chart_data.set_index("Date"))
        else:
            st.info("No data to display.")
