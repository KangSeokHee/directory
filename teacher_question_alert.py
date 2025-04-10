
import streamlit as st
import sqlite3
import pandas as pd

DB_NAME = "students.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS questions (student TEXT, date TEXT, question TEXT, is_read INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()

def fetch_questions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT rowid, student, date, question, is_read FROM questions ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def mark_as_read(rowid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE questions SET is_read=1 WHERE rowid=?", (rowid,))
    conn.commit()
    conn.close()

init_db()
st.set_page_config(page_title="학생 질문 확인", layout="centered")
st.title("❓ 학생 질문 알림")

# 읽지 않은 질문 수 카운트
questions = fetch_questions()
unread_count = sum(1 for q in questions if q[4] == 0)
if unread_count:
    st.warning(f"🔔 읽지 않은 질문 {unread_count}건이 있습니다!")

# 질문 표시
for rowid, student, date, question, is_read in questions:
    if is_read == 0:
        st.markdown(f"**[{date}] {student}**: {question}")
        if st.button(f"✅ 읽음 처리 - {rowid}", key=f"btn_{rowid}"):
            mark_as_read(rowid)
            st.rerun()
    else:
        with st.expander(f"[{date}] {student} (읽음)"):
            st.write(question)
