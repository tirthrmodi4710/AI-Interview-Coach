def evaluate_answer(question, answer):

    if len(answer.strip()) < 20:
        score = 40
        feedback = "Your answer is too short. Try to explain in more detail."

    elif len(answer.strip()) < 50:
        score = 70
        feedback = "Good attempt. Add more technical details."

    else:
        score = 90
        feedback = "Good answer with sufficient explanation."

    return {
        "score": score,
        "feedback": feedback
    }