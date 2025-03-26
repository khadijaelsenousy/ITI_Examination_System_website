import streamlit as st
import pyodbc


st.set_page_config(page_title="Instructor page", layout="centered")


def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=KHADIJAA;'  
        'DATABASE=Examination_system;'  
        'Trusted_Connection=yes;'
    )
    return conn

def get_next_exam_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ISNULL(MAX(Exam_ID), 0) + 1 FROM Exam;")  
    next_exam_id = cursor.fetchone()[0]
    conn.close()
    return next_exam_id


if "user_id" not in st.session_state or st.session_state["user_role"] != "instructor":
    st.error("🚫 Access Denied. Please log in as an instructor.")
    st.stop()

st.markdown(
    """
    <style>
    .stTextInput>div>div>input {
        font-size: 18px;
        padding: 8px;
    }
    .stNumberInput>div>div>input {
        font-size: 18px;
        padding: 8px;
    }
    .stButton>button {
        font-size: 20px;
        background-color: #a70000;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True
)


st.title("🎓 Instructor page")
st.subheader("📝 Generate an Exam")

next_exam_id = get_next_exam_id()
st.markdown(f'<div style="background-color:#e8f4ff;padding:10px;border-radius:10px;font-size:20px;">✅ Auto-generated Exam ID: <b>{next_exam_id}</b></div>', unsafe_allow_html=True)


col1, col2 = st.columns(2)
course_id = col1.text_input("📚 Course ID:")
exam_duration = col2.number_input("⏳ Exam Duration (minutes):", min_value=1)

num_questions = st.number_input("❓ Number of Questions:", min_value=1)

if st.button(" Generate Exam"):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC GenerateExam ?, ?, ?, ?, ?", 
                       (next_exam_id, course_id, exam_duration, num_questions, st.session_state["user_id"]))
        conn.commit()
        st.success(f"🎉 Exam {next_exam_id} generated successfully!")
    except Exception as e:
        st.error(f"❌ Error: {e}")
    finally:
        conn.close()

