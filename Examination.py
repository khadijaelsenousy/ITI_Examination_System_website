import streamlit as st
import pyodbc


def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=KHADIJAA;'  
        'DATABASE=Examination_system;'  
        'Trusted_Connection=yes;'
    )
    return conn



st.set_page_config(page_title="ITI Examination System")


st.markdown("<h1 style='text-align: center;'>ITI Examination System</h1>", unsafe_allow_html=True)


st.markdown("""
    <style>
        .stButton>button {
            background-color: #8B0000; /* ITI Red */
            color: white;
            font-size: 18px;
            border-radius: 8px;
            padding: 12px 20px;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)



def main():
    st.image("logo4.png", width=700)
    st.markdown("<h1 style='color: #8B0000;'></h1>", unsafe_allow_html=True)
    
    role = st.radio("Select Role:", ["Student", "Instructor"])
    user_input_id = st.text_input("User ID:")  
    
    if st.button("Login"):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if role == "Instructor":
            cursor.execute("SELECT * FROM Instructor WHERE Inst_ID = ?", (user_input_id,))
        else:
            cursor.execute("SELECT * FROM Student WHERE St_ID = ?", (user_input_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            
            st.session_state["user_id"] = user_input_id
            st.session_state["user_role"] = role.lower()
            st.success(f"Logged in as {role}")
            
            if role == "Instructor":
                st.switch_page("pages/instructor.py")
            else:
                st.switch_page("pages/student.py")
        else:
            st.error("Invalid ID")
    
if __name__ == "__main__":
    main()


