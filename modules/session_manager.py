import streamlit as st


def initialize_session():

    defaults = {
        # Auth
        "logged_in": False,
        "user": None,

        # Interview
        "interview_started": False,
        "interview_completed": False,
        "show_evaluation": False,
        "answers": [],
        "scores": [],
        "questions": [],
        "evaluation_results": [],
        "current_question_index": 0,
        "evaluation_result": None,
        "current_answer": "",
        "webcam_results": [],
        "candidate_name": "",
        "_interview_saved": False,

        # Proctoring
        "proctoring_log": [],
        "auto_snapshots": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_interview():
    """Resets only interview state, preserving auth."""
    defaults = {
        "interview_started": False,
        "interview_completed": False,
        "show_evaluation": False,
        "answers": [],
        "scores": [],
        "questions": [],
        "evaluation_results": [],
        "current_question_index": 0,
        "evaluation_result": None,
        "current_answer": "",
        "webcam_results": [],
        "_interview_saved": False,
        "proctoring_log": [],
        "auto_snapshots": [],
    }
    for key, value in defaults.items():
        st.session_state[key] = value