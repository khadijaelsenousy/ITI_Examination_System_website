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


def load_exams():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Exam_ID, CONCAT('Exam ', Exam_ID, ' - Course ', Course_ID, ' (Duration: ', Exam_Duration, ' min)')
        FROM Exam;
    """)
    exams = cursor.fetchall()
    conn.close()
    return {str(exam[0]): exam[1] for exam in exams}

def load_exam_questions(exam_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT Q.Ques_ID, Q.Ques_Text, C.Choice_Text, 
               CHAR(65 + ROW_NUMBER() OVER (PARTITION BY Q.Ques_ID ORDER BY C.Choice_ID) - 1) AS choice_letter 
        FROM Exam_Questions EQ
        JOIN Questions Q ON EQ.Ques_ID = Q.Ques_ID
        JOIN Choices C ON Q.Ques_ID = C.Ques_ID
        WHERE EQ.Exam_ID = ?;
    """, (exam_id,))
    
    questions = {}
    for row in cursor.fetchall():
        ques_id, ques_text, choice_text, choice_letter = row
        if ques_id not in questions:
            questions[ques_id] = {"text": ques_text, "choices": {}}
        questions[ques_id]["choices"][choice_letter] = choice_text
    
    conn.close()
    return questions

def submit_answers(student_id, exam_id, answers):
    conn = get_db_connection()
    cursor = conn.cursor()

    for ques_id, student_answer_letter in answers.items():
        
        cursor.execute("""
            SELECT Choice_Text, 
                   CHAR(65 + ROW_NUMBER() OVER (PARTITION BY Ques_ID ORDER BY Choice_ID) - 1) AS choice_letter
            FROM Choices 
            WHERE Ques_ID = ?;
        """, (ques_id,))
        
        choices = cursor.fetchall()
        
        
        choice_text = None
        for choice in choices:
            if choice[1] == student_answer_letter:  
                choice_text = choice[0]
                break

        if choice_text:
            cursor.execute("""
                INSERT INTO Exam_Student (Exam_ID, St_ID, Ques_ID, St_Answer)
                VALUES (?, ?, ?, ?);
            """, (exam_id, student_id, ques_id, choice_text))  

    conn.commit()
    conn.close()






def correct_exam(exam_id, student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC CorrectExam ?, ?", (exam_id, student_id))
    result = cursor.fetchone()
    conn.close()
    
    if result and hasattr(result, 'FinalScore'):
        return f"✅Exam corrected successfully! Your final score is: {result.FinalScore}"
    return "Exam corrected successfully! No score available."

# Streamlit UI
def main():
    st.image("logo4.png", use_container_width=True)
    st.title("📚 Student page")

    student_id = st.session_state.get("user_id")
    if not student_id:
        st.error("You must log in first!")
        return

    exams = load_exams()
    
    
    exam_id = st.selectbox("Select an exam:", options=list(exams.keys()), format_func=lambda x: exams[x])
    
    if st.button("📝Take Exam"):
        st.session_state["selected_exam"] = exam_id
        st.rerun()

    
    if "selected_exam" in st.session_state:
        exam_id = st.session_state["selected_exam"]
        st.subheader(f"You are taking {exams[exam_id]}")
        
        questions = load_exam_questions(exam_id)
        student_answers = {}

        for ques_id, data in questions.items():
            st.write(f"**Q{ques_id}: {data['text']}**")
            student_answers[ques_id] = st.radio(
                "Choose an answer:", 
                options=list(data["choices"].keys()), 
                format_func=lambda x: f"{x}) {data['choices'][x]}",
                key=f"q{ques_id}",
                index=None  
            )

        if st.button("Submit Answers"):
            submit_answers(student_id, exam_id, student_answers)
            result_message = correct_exam(exam_id, student_id)
            st.success(result_message)

if __name__ == "__main__":
    main()
