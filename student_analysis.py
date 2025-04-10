
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

DB_NAME = "students.db"

def get_student_info(email, pw):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, grade FROM students WHERE email=? AND password=?", (email, pw))
    result = c.fetchone()
    conn.close()
    return result

def get_scores(student):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT test_name, score FROM scores WHERE student=?", (student,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_attendance(student):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT status FROM attendance WHERE name=?", (student,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_assignments(student):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT submitted FROM assignments WHERE student=?", (student,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def analyze_level(scores, attendance, assignments):
    if not scores:
        return "데이터 부족"
    avg_score = sum([s for _, s in scores]) / len(scores)
    attend_count = Counter(attendance)
    submit_rate = sum(assignments) / len(assignments) if assignments else 0

    if avg_score >= 90 and attend_count.get("결석", 0) < 2 and submit_rate > 0.8:
        return "우수"
    elif avg_score >= 75:
        return "안정"
    elif avg_score >= 60:
        return "주의"
    else:
        return "위험"

st.set_page_config(page_title="학습 분석", layout="wide")
st.title("📈 나의 학습 분석 리포트")

if "student" not in st.session_state:
    st.subheader("로그인")
    email = st.text_input("이메일")
    pw = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        info = get_student_info(email, pw)
        if info:
            st.session_state.student = info[0]
            st.session_state.grade = info[1]
            st.rerun()
        else:
            st.error("로그인 실패")
    st.stop()

name = st.session_state.student
st.subheader(f"{name}님의 학습 리포트")

# 데이터 가져오기
scores = get_scores(name)
attendance = get_attendance(name)
assignments = get_assignments(name)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 시험 성적 추이")
    if scores:
        df = pd.DataFrame(scores, columns=["시험명", "점수"])
        fig, ax = plt.subplots()
        ax.plot(df["시험명"], df["점수"], marker='o')
        ax.set_ylim(0, 100)
        st.pyplot(fig)
    else:
        st.info("성적 데이터가 없습니다.")

with col2:
    st.markdown("### 출결 현황")
    count = Counter(attendance)
    if count:
        fig2, ax2 = plt.subplots()
        ax2.bar(count.keys(), count.values(), color='gray')
        st.pyplot(fig2)
    else:
        st.info("출결 데이터가 없습니다.")

# 과제 제출률
st.markdown("### 과제 제출률")
if assignments:
    total = len(assignments)
    submitted = sum(assignments)
    fig3, ax3 = plt.subplots()
    ax3.pie([submitted, total-submitted], labels=["제출", "미제출"], autopct="%1.1f%%", startangle=90, colors=["green", "lightgray"])
    ax3.axis("equal")
    st.pyplot(fig3)
else:
    st.info("과제 데이터가 없습니다.")

# AI 분석
st.markdown("### AI 학습 상태 예측")
result = analyze_level(scores, attendance, assignments)
color_map = {"우수": "🟢", "안정": "🟡", "주의": "🟠", "위험": "🔴", "데이터 부족": "⚪"}
st.success(f"{color_map.get(result, '❓')} 예측 학습 상태: **{result}**")
