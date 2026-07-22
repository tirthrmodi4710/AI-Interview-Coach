from datetime import datetime
from modules.supabase_client import supabase

def initialize_db():
    """
    Database initialization is handled by Supabase.
    This function is kept only for compatibility with app.py.
    """
    pass

def save_interview(user_id, data):
    """
    Saves a completed interview to Supabase.
    """

    try:
        supabase.table("interview_sessions").insert({
            "user_id": user_id,
            "candidate_name": data.get("candidate_name", ""),
            "role": data.get("role", ""),
            "level": data.get("level", ""),
            "interview_type": data.get("interview_type", ""),
            "evaluation_mode": data.get("evaluation_mode", ""),
            "question_source": data.get("question_source", ""),
            "total_questions": data.get("total_questions", 0),
            "average_score": data.get("average_score", 0),
            "technical_score": data.get("technical_score", 0),
            "communication_score": data.get("communication_score", 0),
            "confidence_score": data.get("confidence_score", 0),
            "band": data.get("band", ""),
            "scores": data.get("scores", []),
            "questions": data.get("questions", []),
            "answers": data.get("answers", []),
            "evaluation_results": data.get("evaluation_results", [])
        }).execute()

        return True

    except Exception as e:
        print(f"Supabase Save Error: {e}")
        return False
    

def get_user_interviews(user_id):
    """
    Returns all interviews for a user from Supabase.
    """

    try:
        response = (
            supabase
            .table("interview_sessions")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        interviews = response.data or []

        for interview in interviews:

            created = datetime.fromisoformat(
                interview["created_at"].replace("Z", "+00:00")
            )

            interview["display_date"] = created.strftime("%d %B %Y")

            interview["scores"] = interview.get("scores") or []
            interview["questions"] = interview.get("questions") or []
            interview["answers"] = interview.get("answers") or []
            interview["evaluation_results"] = interview.get("evaluation_results") or []

        return interviews

    except Exception as e:
        print(f"Supabase Fetch Error: {e}")
        return []

def delete_interview(interview_id, user_id):
    """
    Deletes an interview belonging to the current user.
    """

    try:
        (
            supabase
            .table("interview_sessions")
            .delete()
            .eq("id", interview_id)
            .eq("user_id", user_id)
            .execute()
        )

    except Exception as e:
        print(f"Supabase Delete Error: {e}")