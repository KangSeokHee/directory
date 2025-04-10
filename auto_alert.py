
import sqlite3
from collections import Counter
from statistics import mean
import smtplib
from email.message import EmailMessage

DB_NAME = "students.db"

def get_all_students():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, email FROM students")
    result = c.fetchall()
    conn.close()
    return result

def check_conditions(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 성적
    c.execute("SELECT score FROM scores WHERE student=?", (name,))
    scores = [row[0] for row in c.fetchall()]
    avg_score = mean(scores) if scores else 100

    # 과제
    c.execute("SELECT submitted FROM assignments WHERE student=?", (name,))
    submitted = [row[0] for row in c.fetchall()]
    not_submitted = submitted.count(0)

    # 출결 (최근 7일)
    c.execute("SELECT date, status FROM attendance WHERE name=? ORDER BY date DESC LIMIT 7", (name,))
    recent = [row[1] for row in c.fetchall()]
    absent_count = recent.count("결석")

    conn.close()

    alert = []
    if avg_score < 60:
        alert.append(f"- 평균 성적: {avg_score:.1f}점")
    if not_submitted >= 2:
        alert.append(f"- 미제출 과제: {not_submitted}개")
    if absent_count >= 2:
        alert.append(f"- 최근 결석: {absent_count}회")
    
    return alert

def send_email_alert(to_email, student_name, alerts):
    msg = EmailMessage()
    msg["Subject"] = "[식키수학연구소] 학습 상태 알림"
    msg["From"] = "your_email@gmail.com"
    msg["To"] = to_email

    body = f"""{student_name} 학생의 최근 학습 상태에 주의가 필요합니다.

""" + "
".join(alerts)
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("your_email@gmail.com", "your_password")
        smtp.send_message(msg)

# 실행
students = get_all_students()
for name, email in students:
    alerts = check_conditions(name)
    if alerts:
        send_email_alert(email, name, alerts)
        print(f"{name} 알림 전송됨.")
