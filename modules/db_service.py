import sqlite3
import os
import json
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "interview_coach.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    """
    Creates all required tables if they don't exist.
    Called once at app startup.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Interview history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            candidate_name TEXT,
            role TEXT,
            level TEXT,
            interview_type TEXT,
            evaluation_mode TEXT,
            question_source TEXT,
            total_questions INTEGER,
            average_score REAL,
            technical_score REAL,
            communication_score REAL,
            confidence_score REAL,
            band TEXT,
            scores TEXT,
            questions TEXT,
            answers TEXT,
            evaluation_results TEXT,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def save_interview(user_id, data):
    """
    Saves a completed interview to the database.
    data dict keys: candidate_name, role, level, interview_type,
    evaluation_mode, question_source, total_questions, average_score,
    technical_score, communication_score, confidence_score, band,
    scores, questions, answers, evaluation_results
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interviews (
            user_id, candidate_name, role, level, interview_type,
            evaluation_mode, question_source, total_questions,
            average_score, technical_score, communication_score,
            confidence_score, band, scores, questions, answers,
            evaluation_results, date
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        user_id,
        data.get("candidate_name", ""),
        data.get("role", ""),
        data.get("level", ""),
        data.get("interview_type", ""),
        data.get("evaluation_mode", ""),
        data.get("question_source", ""),
        data.get("total_questions", 0),
        data.get("average_score", 0),
        data.get("technical_score", 0),
        data.get("communication_score", 0),
        data.get("confidence_score", 0),
        data.get("band", ""),
        json.dumps(data.get("scores", [])),
        json.dumps(data.get("questions", [])),
        json.dumps(data.get("answers", [])),
        json.dumps(data.get("evaluation_results", [])),
        datetime.date.today().strftime("%d %B %Y")
    ))

    conn.commit()
    conn.close()


def get_user_interviews(user_id):
    """
    Returns all interviews for a given user, newest first.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM interviews
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    interviews = []
    for row in rows:
        item = dict(row)
        item["scores"] = json.loads(item["scores"] or "[]")
        item["questions"] = json.loads(item["questions"] or "[]")
        item["answers"] = json.loads(item["answers"] or "[]")
        item["evaluation_results"] = json.loads(item["evaluation_results"] or "[]")
        interviews.append(item)

    return interviews


def delete_interview(interview_id, user_id):
    """
    Deletes a specific interview — only if it belongs to the user.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, user_id)
    )
    conn.commit()
    conn.close()