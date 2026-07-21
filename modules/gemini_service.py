import os
import json

import google.generativeai as genai


def _get_api_key():
    """
    Reads GEMINI_API_KEY from Streamlit secrets (production)
    or from environment variable (local).
    """
    try:
        import streamlit as st
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("GEMINI_API_KEY")


def _get_model():
    api_key = _get_api_key()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


def test_gemini():
    model = _get_model()
    response = model.generate_content("Say hello in one sentence.")
    return response.text


def generate_questions(role, level, interview_type, num_questions):

    model = _get_model()

    prompt = f"""
You are an expert technical interviewer.

Generate exactly {num_questions} interview questions for the following:

Role: {role}
Experience Level: {level}
Interview Type: {interview_type}

Rules:
- Questions must be appropriate for the {level} level
- Questions must be relevant to {role}
- If interview type is Technical, focus on technical concepts
- If interview type is HR, focus on behavioural and situational questions
- If interview type is Mixed, include both technical and behavioural questions
- Each question should be clear and concise
- Do not number the questions
- Respond ONLY with a valid JSON array of strings
- No explanation, no markdown, no code fences. Just the raw JSON array.

Example format:
["Question one?", "Question two?", "Question three?"]
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        questions = json.loads(raw)
        if not isinstance(questions, list):
            raise ValueError("Response is not a list")
        questions = [str(q) for q in questions]
        questions = questions[:num_questions]
        return questions
    except (json.JSONDecodeError, ValueError):
        return [f"Tell me about your experience as a {role}."] * num_questions


def evaluate_with_gemini(question, answer):

    model = _get_model()

    prompt = f"""
You are an expert technical interviewer.

Question:
{question}

Candidate Answer:
{answer}

Evaluate the answer and respond ONLY with a valid JSON object.
No explanation, no markdown, no code fences. Just the raw JSON.

The JSON must follow this exact structure:
{{
  "score": <integer from 0 to 100>,
  "feedback": "<what the candidate did well>",
  "missing_points": "<what was missing or incorrect>",
  "ideal_answer": "<a concise ideal answer to the question>"
}}
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        parsed = json.loads(raw)
        return {
            "score": int(parsed.get("score", 0)),
            "feedback": parsed.get("feedback", "No feedback provided."),
            "missing_points": parsed.get("missing_points", ""),
            "ideal_answer": parsed.get("ideal_answer", "")
        }
    except (json.JSONDecodeError, ValueError):
        return {
            "score": 0,
            "feedback": raw,
            "missing_points": "Could not parse structured response.",
            "ideal_answer": ""
        }