
import streamlit as st
import sqlite3

DB_NAME = "students.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS graded_assignments (title TEXT, questions INTEGER, answers TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS student_answers (student TEXT, title TEXT, answers TEXT, score INTEGER)")
    conn.commit()
    conn.close()

def add_assignment(title, questions, answers):
    answers_str = ",".join(str(a) for a in answers)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO graded_assignments (title, questions, answers) VALUES (?, ?, ?)", (title, questions, answers_str))
    conn.commit()
    conn.close()

def get_assignments():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT title, questions FROM graded_assignments")
    rows = c.fetchall()
    conn.close()
    return rows

def get_answer_key(title):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT answers FROM graded_assignments WHERE title=?", (title,))
    row = c.fetchone()
    conn.close()
    return [int(x) for x in row[0].split(",")] if row else []

def submit_answers(student, title, student_answers):
    answer_key = get_answer_key(title)
    score = sum([1 for i, a in enumerate(student_answers) if i < len(answer_key) and a == answer_key[i]])
    answers_str = ",".join(str(a) for a in student_answers)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO student_answers (student, title, answers, score) VALUES (?, ?, ?, ?)", (student, title, answers_str, score))
    conn.commit()
    conn.close()
    return score

init_db()
st.set_page_config(page_title="자동 채점 과제 시스템")

st.title("✏️ 자동 채점 과제 시스템")

menu = st.sidebar.radio("모드 선택", ["📘 선생님 - 과제 출제", "🧑‍🎓 학생 - 과제 제출"])

if menu == "📘 선생님 - 과제 출제":
    st.subheader("📘 과제 출제")
    title = st.text_input("과제명 입력")
    num_questions = st.number_input("문항 수", min_value=1, max_value=50, value=5, step=1)
    answers = []
    for i in range(int(num_questions)):
        answers.append(st.number_input(f"{i+1}번 정답 (1~5)", min_value=1, max_value=5, key=f"q{i}"))

    if st.button("✅ 과제 등록"):
        if title and len(answers) == int(num_questions):
            add_assignment(title, int(num_questions), answers)
            st.success("과제가 등록되었습니다.")
        else:
            st.error("모든 문항 정답을 입력해주세요.")

elif menu == "🧑‍🎓 학생 - 과제 제출":
    st.subheader("🧑‍🎓 과제 제출 및 채점")
    student_name = st.text_input("학생 이름 입력")
    assignments = get_assignments()
    if assignments:
        titles = [a[0] for a in assignments]
        selected = st.selectbox("과제 선택", titles)
        question_count = [a[1] for a in assignments if a[0] == selected][0]
        student_answers = []
        for i in range(int(question_count)):
            student_answers.append(st.number_input(f"{i+1}번 답 (1~5)", min_value=1, max_value=5, key=f"stu_{i}"))

        if st.button("📩 제출 및 채점"):
            if student_name and student_answers:
                score = submit_answers(student_name, selected, student_answers)
                st.success(f"{student_name}님의 점수는 {score} / {question_count}점입니다.")
            else:
                st.warning("이름과 모든 문항을 입력해주세요.")
    else:
        st.info("출제된 과제가 없습니다.")
