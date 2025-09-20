import streamlit as st
from backend_stub import process_attendance, mark_attendance_camera

st.set_page_config(page_title="Face Attendance Dashboard", layout="wide")

st.title("🎓 Attendance Dashboard")

menu = ["Upload CSV", "Camera Attendance"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Upload CSV":
    st.subheader("Upload New Attendance CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = process_attendance(uploaded_file)
        st.success("✅ File processed successfully!")
        st.dataframe(df)

elif choice == "Camera Attendance":
    st.subheader("Mark Attendance Using Camera")
    if st.button("Start Camera"):
        result = mark_attendance_camera()
        if isinstance(result, str):
            st.error(result)
        else:
            st.success("✅ Attendance marked!")
            st.dataframe(result)
