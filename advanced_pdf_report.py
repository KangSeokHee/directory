
from fpdf import FPDF
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime
import smtplib
from email.message import EmailMessage
import os

DB_NAME = "students.db"

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "식키수학연구소 - 월간 리포트", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def draw_score_chart(scores, student_name):
    tests, values = zip(*scores)
    plt.figure(figsize=(6, 3))
    plt.plot(tests, values, marker='o')
    plt.title(f"{student_name} 성적 추이")
    plt.ylabel("점수")
    plt.ylim(0, 100)
    plt.tight_layout()
    filename = f"{student_name}_score_chart.png"
    plt.savefig(filename)
    plt.close()
    return filename

def draw_attendance_chart(attendance, student_name):
    from collections import Counter
    status_count = Counter([s for d, s in attendance])
    labels, counts = zip(*status_count.items())
    plt.figure(figsize=(4, 3))
    plt.bar(labels, counts, color='gray')
    plt.title("출결 현황")
    plt.tight_layout()
    filename = f"{student_name}_attendance_chart.png"
    plt.savefig(filename)
    plt.close()
    return filename

def predict_performance(scores):
    if not scores:
        return "데이터 부족"
    last_scores = [s for _, s in scores[-3:]]
    avg = sum(last_scores) / len(last_scores)
    if avg >= 90:
        return "매우 우수"
    elif avg >= 75:
        return "안정"
    elif avg >= 60:
        return "주의"
    else:
        return "위험"

def generate_pdf_report(student_name, email, filename="report.pdf"):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    pdf.cell(0, 10, f"학생 이름: {student_name}", ln=True)
    pdf.cell(0, 10, f"이메일: {email}", ln=True)

    # 성적
    c.execute("SELECT test_name, score FROM scores WHERE student=?", (student_name,))
    scores = c.fetchall()
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "성적 요약", ln=True)
    pdf.set_font("Arial", "", 12)
    for test_name, score in scores:
        pdf.cell(0, 10, f"{test_name}: {score}점", ln=True)

    chart1 = draw_score_chart(scores, student_name)
    pdf.image(chart1, x=10, w=180)

    # 출결
    c.execute("SELECT date, status FROM attendance WHERE name=?", (student_name,))
    attendance = c.fetchall()
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "출결 기록", ln=True)
    pdf.set_font("Arial", "", 12)
    for date_str, status in attendance[-10:]:
        pdf.cell(0, 10, f"{date_str} - {status}", ln=True)

    chart2 = draw_attendance_chart(attendance, student_name)
    pdf.image(chart2, x=10, w=140)

    # 상담
    c.execute("SELECT date, category, content FROM counseling WHERE name=?", (student_name,))
    counseling = c.fetchall()
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "상담 요약", ln=True)
    pdf.set_font("Arial", "", 12)
    for date_str, category, content in counseling[-3:]:
        pdf.multi_cell(0, 10, f"{date_str} - [{category}] {content}")

    # AI 분석
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "AI 학습 분석 결과", ln=True)
    result = predict_performance(scores)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"예상 학습 상태: {result}", ln=True)

    conn.close()
    pdf.output(filename)
    os.remove(chart1)
    os.remove(chart2)

def send_email_report(email, filename):
    msg = EmailMessage()
    msg["Subject"] = "식키수학연구소 월간 리포트"
    msg["From"] = "your_email@gmail.com"
    msg["To"] = email
    msg.set_content("첨부된 PDF 리포트를 확인해주세요.")

    with open(filename, "rb") as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=filename)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("your_email@gmail.com", "your_password")  # 비밀번호 앱 비밀번호 사용
        smtp.send_message(msg)
