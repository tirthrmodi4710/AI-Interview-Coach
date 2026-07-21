def get_interview_shell(total_questions, duration_seconds, question_index, questions, answers, webcam_enabled=True):
    """
    Returns a full-page interview shell HTML that mimics Mercer Mettl:
    - Fixed top navbar with timer and question counter
    - Left panel: question navigator + live webcam feed
    - Right panel: question text + answer textarea
    - Fullscreen enforcement with 3-warning system
    - Tab switch detection and copy-paste detection
    - Auto webcam snapshots every 2 minutes
    - All events pushed to URL query params for Streamlit to read

    This component communicates back to Streamlit via:
    - ?proctor_events=... for tab/paste/fullscreen events
    - ?voice_answer=... for answer text
    - ?nav_to=... for question navigation clicks
    - ?timer_expired=1 for auto-submit when timer hits 0
    """

    q_nav_html = ""
    for i, q in enumerate(questions):
        is_answered = i < len(answers)
        is_current = i == question_index
        if is_current:
            state_class = "nav-current"
            icon = "▶"
        elif is_answered:
            state_class = "nav-answered"
            icon = "✓"
        else:
            state_class = "nav-unanswered"
            icon = str(i + 1)
        q_nav_html += f"""
        <div class="nav-item {state_class}" onclick="navigateTo({i})">
            <span class="nav-icon">{icon}</span>
            <span class="nav-text">Q{i+1}: {q[:35]}{'...' if len(q) > 35 else ''}</span>
        </div>
        """

    current_q = questions[question_index] if question_index < len(questions) else ""
    current_a = answers[question_index] if question_index < len(answers) else ""

    webcam_html = ""
    if webcam_enabled:
        webcam_html = """
        <div class="webcam-container">
            <div class="webcam-header">
                <span class="rec-dot"></span>
                <span style="font-size:12px; font-weight:500; color:#374151;">Camera Active</span>
                <span style="margin-left:auto; font-size:11px; color:#6B7280;">Auto-snapshot every 2min</span>
            </div>
            <video id="webcamFeed" autoplay playsinline muted
                style="width:100%; border-radius:8px; background:#0a0a0f; min-height:140px; object-fit:cover;">
            </video>
            <canvas id="snapCanvas" style="display:none;"></canvas>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #F8FAFC;
        color: #111827;
        height: 100%;
        min-height: 860px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }}

    /* ── Animations ────────────────────────────────────────────────────────── */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(-12px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.5; transform: scale(0.9); }}
    }}

    @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.2; }}
    }}

    /* ── Scrollbar ─────────────────────────────────────────────────────────── */
    ::-webkit-scrollbar {{
        width: 4px;
        height: 4px;
    }}

    ::-webkit-scrollbar-track {{
        background: #F1F5F9;
        border-radius: 2px;
    }}

    ::-webkit-scrollbar-thumb {{
        background: #2563EB;
        border-radius: 2px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: #1E40AF;
    }}

    /* ── Top Navbar ──────────────────────────────────────────────────────────── */
    .navbar {{
        background: #FFFFFF;
        border-bottom: 2px solid #E5E7EB;
        padding: 0 28px;
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        flex-shrink: 0;
        z-index: 100;
        animation: fadeIn 0.3s ease-out;
    }}

    .navbar-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 800;
        font-size: 18px;
        color: #111827;
        letter-spacing: -0.02em;
    }}

    .navbar-brand span {{
        color: #2563EB;
    }}

    .navbar-brand-icon {{
        font-size: 20px;
    }}

    .navbar-center {{
        display: flex;
        align-items: center;
        gap: 24px;
    }}

    .timer-box {{
        display: flex;
        align-items: center;
        gap: 8px;
        background: #F1F5F9;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 8px 18px;
        font-weight: 700;
        font-size: 15px;
        color: #1E40AF;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        min-width: 85px;
        justify-content: center;
    }}

    .timer-box.urgent {{
        background: #FEF2F2;
        border-color: #FCA5A5;
        color: #991B1B;
        animation: pulse 1s ease-in-out infinite;
    }}

    .timer-icon {{
        font-size: 16px;
    }}

    .q-counter {{
        font-size: 13px;
        color: #6B7280;
        font-weight: 500;
        background: #F1F5F9;
        padding: 6px 16px;
        border-radius: 99px;
        border: 1px solid #E5E7EB;
    }}

    .navbar-right {{
        display: flex;
        align-items: center;
        gap: 16px;
    }}

    .candidate-badge {{
        font-size: 13px;
        color: #374151;
        font-weight: 500;
        background: #F1F5F9;
        padding: 6px 14px;
        border-radius: 99px;
        display: flex;
        align-items: center;
        gap: 6px;
        border: 1px solid #E5E7EB;
    }}

    .submit-btn {{
        background: #2563EB;
        color: white;
        border: none;
        padding: 8px 24px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.12);
        position: relative;
        overflow: hidden;
    }}

    .submit-btn::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        opacity: 0;
        transition: opacity 0.2s ease;
    }}

    .submit-btn:hover {{
        background: #1E40AF;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
    }}

    .submit-btn:hover::before {{
        opacity: 1;
    }}

    .submit-btn:active {{
        transform: translateY(0px);
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.15);
    }}

    /* ── Main Layout ────────────────────────────────────────────────────────── */
    .main-layout {{
        display: flex;
        flex: 1;
        overflow: hidden;
        animation: fadeIn 0.4s ease-out;
    }}

    /* ── Left Panel ─────────────────────────────────────────────────────────── */
    .left-panel {{
        width: 300px;
        background: #FFFFFF;
        border-right: 2px solid #E5E7EB;
        display: flex;
        flex-direction: column;
        flex-shrink: 0;
        overflow: hidden;
    }}

    .panel-section-title {{
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6B7280;
        padding: 16px 20px 10px;
        border-bottom: 1px solid #F1F5F9;
    }}

    .nav-list {{
        flex: 1;
        overflow-y: auto;
        padding: 8px 0 12px;
    }}

    .nav-item {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 20px;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 3px solid transparent;
        position: relative;
    }}

    .nav-item:hover {{
        background: #F8FAFC;
    }}

    .nav-item:active {{
        transform: scale(0.98);
    }}

    .nav-current {{
        background: #EFF6FF !important;
        border-left-color: #2563EB !important;
    }}

    .nav-answered {{
        border-left-color: #10B981;
    }}

    .nav-unanswered {{
        border-left-color: transparent;
    }}

    .nav-icon {{
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 700;
        flex-shrink: 0;
        transition: all 0.2s ease;
    }}

    .nav-current .nav-icon {{
        background: #2563EB;
        color: white;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
    }}

    .nav-answered .nav-icon {{
        background: #10B981;
        color: white;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2);
    }}

    .nav-unanswered .nav-icon {{
        background: #F1F5F9;
        color: #6B7280;
        border: 1px solid #E5E7EB;
    }}

    .nav-item:hover .nav-unanswered .nav-icon {{
        background: #E5E7EB;
        border-color: #D1D5DB;
    }}

    .nav-text {{
        font-size: 13px;
        color: #374151;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-weight: 500;
        transition: color 0.2s ease;
    }}

    .nav-current .nav-text {{
        color: #1E40AF;
        font-weight: 600;
    }}

    .nav-answered .nav-text {{
        color: #065F46;
    }}

    /* ── Webcam ────────────────────────────────────────────────────────────── */
    .webcam-container {{
        border-top: 2px solid #E5E7EB;
        padding: 16px 20px 20px;
        background: #F8FAFC;
    }}

    .webcam-header {{
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
    }}

    .rec-dot {{
        width: 10px;
        height: 10px;
        background: #EF4444;
        border-radius: 50%;
        animation: blink 1.2s ease-in-out infinite;
        box-shadow: 0 0 8px rgba(239, 68, 68, 0.4);
    }}

    /* ── Right Panel ───────────────────────────────────────────────────────── */
    .right-panel {{
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        padding: 28px 32px;
        background: #F8FAFC;
    }}

    .question-card {{
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
        animation: slideIn 0.3s ease-out;
        border-left: 4px solid #2563EB;
    }}

    .question-card:hover {{
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border-color: #D1D5DB;
    }}

    .question-label {{
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #2563EB;
        margin-bottom: 10px;
    }}

    .question-text {{
        font-size: 16px;
        font-weight: 500;
        color: #111827;
        line-height: 1.7;
    }}

    .answer-card {{
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 24px 28px;
        flex: 1;
        display: flex;
        flex-direction: column;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
        animation: fadeIn 0.4s ease-out;
    }}

    .answer-card:hover {{
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }}

    .answer-label {{
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6B7280;
        margin-bottom: 12px;
    }}

    .answer-textarea {{
        flex: 1;
        width: 100%;
        border: 2px solid #E5E7EB;
        border-radius: 12px;
        padding: 16px;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: #111827;
        resize: none;
        outline: none;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 200px;
        background: #FFFFFF;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        line-height: 1.6;
    }}

    .answer-textarea::placeholder {{
        color: #9CA3AF;
        font-weight: 400;
    }}

    .answer-textarea:focus {{
        border-color: #2563EB;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1), 0 1px 2px rgba(0,0,0,0.04);
    }}

    .answer-textarea:focus::placeholder {{
        color: #D1D5DB;
    }}

    .answer-footer {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #F1F5F9;
    }}

    .char-count {{
        font-size: 12px;
        color: #6B7280;
        font-weight: 500;
    }}

    .nav-btns {{
        display: flex;
        gap: 10px;
    }}

    .btn-prev {{
        background: #F1F5F9;
        color: #111827;
        border: 1px solid #E5E7EB;
        padding: 9px 22px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }}

    .btn-prev:hover {{
        background: #E5E7EB;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }}

    .btn-prev:active {{
        transform: translateY(0px);
    }}

    .btn-next {{
        background: #2563EB;
        color: white;
        border: none;
        padding: 9px 28px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.12);
        position: relative;
        overflow: hidden;
    }}

    .btn-next::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        opacity: 0;
        transition: opacity 0.2s ease;
    }}

    .btn-next:hover {{
        background: #1E40AF;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
    }}

    .btn-next:hover::before {{
        opacity: 1;
    }}

    .btn-next:active {{
        transform: translateY(0px);
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.15);
    }}

    .btn-next:disabled {{
        background: #D1D5DB;
        cursor: not-allowed;
        transform: none !important;
        box-shadow: none !important;
    }}

    .btn-next:disabled::before {{
        display: none;
    }}

    /* ── Warning Overlay ────────────────────────────────────────────────────── */
    .warning-overlay {{
        display: none;
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.6);
        backdrop-filter: blur(4px);
        z-index: 9999;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease-out;
    }}

    .warning-overlay.show {{ display: flex; }}

    .warning-box {{
        background: #FFFFFF;
        border-radius: 20px;
        padding: 40px 44px;
        max-width: 440px;
        width: 90%;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        animation: scaleIn 0.3s ease-out;
    }}

    @keyframes scaleIn {{
        from {{ opacity: 0; transform: scale(0.95); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}

    .warning-icon {{
        font-size: 56px;
        margin-bottom: 16px;
    }}

    .warning-title {{
        font-size: 20px;
        font-weight: 700;
        color: #991B1B;
        margin-bottom: 12px;
        letter-spacing: -0.02em;
    }}

    .warning-msg {{
        font-size: 14px;
        color: #6B7280;
        margin-bottom: 24px;
        line-height: 1.6;
    }}

    .warning-count {{
        font-size: 13px;
        color: #EF4444;
        font-weight: 600;
        margin-bottom: 24px;
        padding: 8px 16px;
        background: #FEF2F2;
        border-radius: 99px;
        display: inline-block;
    }}

    .warning-ok {{
        background: #2563EB;
        color: white;
        border: none;
        padding: 10px 40px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.12);
    }}

    .warning-ok:hover {{
        background: #1E40AF;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
    }}

    .warning-ok:active {{
        transform: translateY(0px);
    }}

    /* ── Responsive ──────────────────────────────────────────────────────────── */
    @media (max-width: 1024px) {{
        .left-panel {{
            width: 260px;
        }}

        .right-panel {{
            padding: 20px 24px;
        }}

        .question-card {{
            padding: 18px 22px;
        }}

        .answer-card {{
            padding: 18px 22px;
        }}
    }}

    @media (max-width: 768px) {{
        .navbar {{
            padding: 0 16px;
            height: 56px;
            flex-wrap: wrap;
        }}

        .navbar-brand {{
            font-size: 15px;
        }}

        .navbar-center {{
            gap: 12px;
        }}

        .timer-box {{
            font-size: 13px;
            padding: 6px 12px;
            min-width: 70px;
        }}

        .q-counter {{
            font-size: 11px;
            padding: 4px 12px;
        }}

        .candidate-badge {{
            display: none;
        }}

        .submit-btn {{
            padding: 6px 16px;
            font-size: 12px;
        }}

        .main-layout {{
            flex-direction: column;
        }}

        .left-panel {{
            width: 100%;
            max-height: 200px;
            border-right: none;
            border-bottom: 2px solid #E5E7EB;
        }}

        .nav-list {{
            display: flex;
            overflow-x: auto;
            padding: 8px 12px;
            gap: 4px;
        }}

        .nav-item {{
            flex-shrink: 0;
            padding: 8px 14px;
            border-left: none;
            border-bottom: 3px solid transparent;
        }}

        .nav-current {{
            border-left-color: transparent;
            border-bottom-color: #2563EB !important;
        }}

        .nav-answered {{
            border-left-color: transparent;
            border-bottom-color: #10B981 !important;
        }}

        .nav-text {{
            font-size: 12px;
        }}

        .webcam-container {{
            border-top: none;
            border-bottom: 2px solid #E5E7EB;
            padding: 12px 16px;
        }}

        .right-panel {{
            padding: 16px;
        }}

        .question-card {{
            padding: 16px 18px;
            margin-bottom: 12px;
        }}

        .question-text {{
            font-size: 14px;
        }}

        .answer-card {{
            padding: 16px 18px;
        }}

        .answer-textarea {{
            min-height: 140px;
            padding: 12px;
            font-size: 13px;
        }}

        .answer-footer {{
            flex-direction: column;
            gap: 12px;
            align-items: stretch;
        }}

        .nav-btns {{
            justify-content: center;
        }}

        .btn-prev, .btn-next {{
            flex: 1;
            text-align: center;
            padding: 8px 16px;
        }}

        .warning-box {{
            padding: 28px 24px;
        }}

        .warning-title {{
            font-size: 17px;
        }}
    }}

    @media (max-width: 480px) {{
        .navbar {{
            padding: 0 12px;
            height: 50px;
        }}

        .navbar-brand {{
            font-size: 13px;
            gap: 6px;
        }}

        .navbar-brand-icon {{
            font-size: 16px;
        }}

        .timer-box {{
            font-size: 12px;
            padding: 4px 10px;
            min-width: 60px;
        }}

        .q-counter {{
            font-size: 10px;
            padding: 3px 10px;
        }}

        .submit-btn {{
            padding: 5px 12px;
            font-size: 11px;
        }}

        .left-panel {{
            max-height: 160px;
        }}

        .right-panel {{
            padding: 12px;
        }}

        .question-card {{
            padding: 12px 14px;
        }}

        .question-text {{
            font-size: 13px;
        }}

        .answer-card {{
            padding: 12px 14px;
        }}

        .answer-textarea {{
            min-height: 100px;
            padding: 10px;
            font-size: 12px;
        }}
    }}
</style>
</head>
<body>

<!-- Warning Overlay -->
<div class="warning-overlay" id="warningOverlay">
    <div class="warning-box">
        <div class="warning-icon">⚠️</div>
        <div class="warning-title" id="warningTitle">Proctoring Violation</div>
        <div class="warning-msg" id="warningMsg">Please return to the interview window.</div>
        <div class="warning-count" id="warningCount"></div>
        <button class="warning-ok" onclick="dismissWarning()">I Understand</button>
    </div>
</div>

<!-- Navbar -->
<div class="navbar">
    <div class="navbar-brand">
        <span class="navbar-brand-icon">🎯</span>
        AI Interview <span>Coach</span>
    </div>
    <div class="navbar-center">
        <div class="timer-box" id="timerBox">
            <span class="timer-icon">⏱</span>
            <span id="timerDisplay">--:--</span>
        </div>
        <div class="q-counter">
            Question {question_index + 1} of {total_questions}
        </div>
    </div>
    <div class="navbar-right">
        <div class="candidate-badge">👤 Candidate</div>
        <button class="submit-btn" onclick="submitInterview()">Submit Interview</button>
    </div>
</div>

<!-- Main Layout -->
<div class="main-layout">

    <!-- Left Panel -->
    <div class="left-panel">
        <div class="panel-section-title">Question Navigator</div>
        <div class="nav-list">
            {q_nav_html}
        </div>
        {webcam_html}
    </div>

    <!-- Right Panel -->
    <div class="right-panel">

        <div class="question-card">
            <div class="question-label">Question {question_index + 1}</div>
            <div class="question-text" id="questionText">{current_q}</div>
        </div>

        <div class="answer-card">
            <div class="answer-label">Your Answer</div>
            <textarea
                class="answer-textarea"
                id="answerBox"
                placeholder="Type your answer here..."
                onpaste="onPaste()"
                oninput="onAnswerInput()"
            >{current_a}</textarea>
            <div class="answer-footer">
                <span class="char-count" id="charCount">0 characters</span>
                <div class="nav-btns">
                    <button class="btn-prev" onclick="prevQuestion()"
                        {'style="display:none"' if question_index == 0 else ''}>
                        ← Previous
                    </button>
                    <button class="btn-next" id="nextBtn" onclick="nextQuestion()">
                        {'Submit Interview ✓' if question_index == total_questions - 1 else 'Save & Next →'}
                    </button>
                </div>
            </div>
        </div>

    </div>
</div>

<script>
const TOTAL_QUESTIONS = {total_questions};
const CURRENT_IDX = {question_index};
const DURATION_SECS = {duration_seconds};
let warningCount = 0;
const MAX_WARNINGS = 3;
let timerInterval = null;
let remainingSeconds = DURATION_SECS;
let webcamStream = null;
let snapshotInterval = null;

// ── TIMER ────────────────────────────────────────────────────────────────────
function initTimer() {{
    const stored = sessionStorage.getItem("interview_timer_remaining");
    if (stored) {{
        remainingSeconds = parseInt(stored);
    }} else {{
        remainingSeconds = DURATION_SECS;
        sessionStorage.setItem("interview_timer_remaining", remainingSeconds);
    }}
    updateTimerDisplay();
    timerInterval = setInterval(() => {{
        remainingSeconds--;
        sessionStorage.setItem("interview_timer_remaining", remainingSeconds);
        updateTimerDisplay();
        if (remainingSeconds <= 0) {{
            clearInterval(timerInterval);
            pushEvent("timer_expired", {{}});
            submitInterview();
        }}
    }}, 1000);
}}

function updateTimerDisplay() {{
    const m = Math.floor(Math.abs(remainingSeconds) / 60).toString().padStart(2, "0");
    const s = (Math.abs(remainingSeconds) % 60).toString().padStart(2, "0");
    const display = m + ":" + s;
    document.getElementById("timerDisplay").innerText = display;
    const box = document.getElementById("timerBox");
    if (remainingSeconds <= 300) {{
        box.classList.add("urgent");
    }}
}}

// ── FULLSCREEN ───────────────────────────────────────────────────────────────
function requestFullscreen() {{
    try {{
        const el = window.parent.document.documentElement;
        if (el.requestFullscreen) el.requestFullscreen();
        else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
    }} catch(e) {{}}
}}

function handleFullscreenExit() {{
    const doc = window.parent.document;
    if (!doc.fullscreenElement && !doc.webkitFullscreenElement) {{
        warningCount++;
        pushEvent("fullscreen_exit", {{ count: warningCount }});
        if (warningCount >= MAX_WARNINGS) {{
            showWarning(
                "Interview Auto-Submitted",
                "You exited fullscreen " + MAX_WARNINGS + " times. Your interview has been auto-submitted.",
                true
            );
            setTimeout(() => submitInterview(), 3000);
        }} else {{
            showWarning(
                "Fullscreen Required",
                "Please do not exit fullscreen mode during the interview.",
                false
            );
        }}
    }}
}}

try {{
    window.parent.document.addEventListener("fullscreenchange", handleFullscreenExit);
    window.parent.document.addEventListener("webkitfullscreenchange", handleFullscreenExit);
}} catch(e) {{}}

// ── TAB SWITCH ───────────────────────────────────────────────────────────────
let tabSwitchCount = 0;

function handleVisibilityChange() {{
    if (document.hidden) {{
        tabSwitchCount++;
        pushEvent("tab_switch", {{ count: tabSwitchCount }});
        showWarning(
            "Tab Switch Detected",
            "Switching tabs during the interview is not allowed and has been recorded.",
            false
        );
    }}
}}

try {{
    window.parent.document.addEventListener("visibilitychange", handleVisibilityChange);
}} catch(e) {{}}
document.addEventListener("visibilitychange", handleVisibilityChange);

// ── COPY-PASTE ───────────────────────────────────────────────────────────────
function onPaste() {{
    pushEvent("paste_detected", {{ question: CURRENT_IDX }});
}}

// ── WEBCAM ───────────────────────────────────────────────────────────────────
async function initWebcam() {{
    try {{
        webcamStream = await navigator.mediaDevices.getUserMedia({{ video: true }});
        const video = document.getElementById("webcamFeed");
        if (video) video.srcObject = webcamStream;
        snapshotInterval = setInterval(takeAutoSnapshot, 120000);
    }} catch(e) {{}}
}}

function takeAutoSnapshot() {{
    if (!webcamStream) return;
    try {{
        const canvas = document.getElementById("snapCanvas");
        const video = document.getElementById("webcamFeed");
        if (!canvas || !video) return;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0);
        const dataUrl = canvas.toDataURL("image/jpeg", 0.7);
        const snapshots = JSON.parse(
            sessionStorage.getItem("auto_snapshots") || "[]"
        );
        snapshots.push({{
            time: new Date().toISOString(),
            question: CURRENT_IDX,
            image: dataUrl
        }});
        sessionStorage.setItem("auto_snapshots", JSON.stringify(snapshots));
        pushEvent("auto_snapshot", {{ question: CURRENT_IDX, time: new Date().toISOString() }});
    }} catch(e) {{}}
}}

// ── ANSWER ───────────────────────────────────────────────────────────────────
function onAnswerInput() {{
    const txt = document.getElementById("answerBox").value;
    document.getElementById("charCount").innerText = txt.length + " characters";
    sessionStorage.setItem("answer_" + CURRENT_IDX, txt);
}}

function getAnswer() {{
    return document.getElementById("answerBox").value.trim();
}}

// ── NAVIGATION ───────────────────────────────────────────────────────────────
function saveAndNavigate(targetIdx) {{
    const answer = getAnswer();
    if (answer) {{
        sessionStorage.setItem("answer_" + CURRENT_IDX, answer);
    }}
    pushNavigation(targetIdx, answer);
}}

function nextQuestion() {{
    const answer = getAnswer();
    if (!answer) {{
        document.getElementById("answerBox").style.borderColor = "#EF4444";
        document.getElementById("answerBox").placeholder = "⚠️ Please enter your answer before continuing.";
        setTimeout(() => {{
            document.getElementById("answerBox").style.borderColor = "#E5E7EB";
            document.getElementById("answerBox").placeholder = "Type your answer here...";
        }}, 2500);
        return;
    }}
    if (CURRENT_IDX >= TOTAL_QUESTIONS - 1) {{
        submitInterview();
    }} else {{
        saveAndNavigate(CURRENT_IDX + 1);
    }}
}}

function prevQuestion() {{
    if (CURRENT_IDX > 0) {{
        saveAndNavigate(CURRENT_IDX - 1);
    }}
}}

function navigateTo(idx) {{
    saveAndNavigate(idx);
}}

async function submitInterview() {{
    const answer = getAnswer();

    sessionStorage.setItem("answer_" + CURRENT_IDX, answer);

    clearInterval(timerInterval);
    clearInterval(snapshotInterval);

    sessionStorage.removeItem("interview_timer_remaining");

    // Exit fullscreen on the parent document
    try {{
        const parentDoc = window.parent.document;

        if (parentDoc.fullscreenElement) {{
            await parentDoc.exitFullscreen();
        }} else if (parentDoc.webkitFullscreenElement) {{
            parentDoc.webkitExitFullscreen();
        }}
    }} catch (e) {{
        console.error("Error exiting fullscreen:", e);
    }}

    setTimeout(() => {{
        pushNavigation(-1, answer);
    }}, 300);
}}

// ── WARNING ──────────────────────────────────────────────────────────────────
function showWarning(title, msg, final) {{
    document.getElementById("warningTitle").innerText = title;
    document.getElementById("warningMsg").innerText = msg;
    if (!final) {{
        document.getElementById("warningCount").innerText =
            "Warning " + warningCount + " of " + MAX_WARNINGS;
        document.getElementById("warningCount").style.display = "inline-block";
    }} else {{
        document.getElementById("warningCount").style.display = "none";
    }}
    document.getElementById("warningOverlay").classList.add("show");
}}

function dismissWarning() {{
    document.getElementById("warningOverlay").classList.remove("show");
    requestFullscreen();
}}

// ── EVENT PUSHER ─────────────────────────────────────────────────────────────
function pushEvent(type, data) {{
    try {{
        const url = new URL(window.parent.location.href);
        const existing = url.searchParams.get("proctor_events");
        let events = [];
        if (existing) {{
            try {{ events = JSON.parse(decodeURIComponent(existing)); }} catch(e) {{}}
        }}
        events.push({{ type: type, ...data }});
        url.searchParams.set("proctor_events", encodeURIComponent(JSON.stringify(events)));
        window.parent.history.replaceState({{}}, "", url.toString());
    }} catch(e) {{}}
}}

function pushNavigation(targetIdx, answer) {{
    try {{
        const url = new URL(window.parent.location.href);
        url.searchParams.set("nav_to", targetIdx);
        if (answer) {{
            url.searchParams.set("nav_answer", encodeURIComponent(answer));
        }}
        window.parent.history.replaceState({{}}, "", url.toString());

        // Click the hidden Streamlit nav button
        const btns = window.parent.document.querySelectorAll("button");
        for (let btn of btns) {{
            if (btn.innerText.trim() === "NAV_SYNC") {{
                btn.click();
                break;
            }}
        }}
    }} catch(e) {{}}
}}

// ── INIT ─────────────────────────────────────────────────────────────────────
window.onload = function() {{
    initTimer();
    requestFullscreen();
    initWebcam();

    // Restore saved answer if any
    const savedAnswer = sessionStorage.getItem("answer_" + CURRENT_IDX);
    if (savedAnswer && !document.getElementById("answerBox").value) {{
        document.getElementById("answerBox").value = savedAnswer;
    }}
    onAnswerInput();
}};
</script>
</body>
</html>
"""
    return html


def get_integrity_summary(proctoring_log):
    tab_switches = [e for e in proctoring_log if e.get("type") == "tab_switch"]
    paste_events = [e for e in proctoring_log if e.get("type") == "paste_detected"]
    fullscreen_exits = [e for e in proctoring_log if e.get("type") == "fullscreen_exit"]
    auto_snapshots = [e for e in proctoring_log if e.get("type") == "auto_snapshot"]

    tab_count = len(tab_switches)
    paste_questions = list(set([e.get("question", "?") for e in paste_events]))
    fullscreen_count = len(fullscreen_exits)

    tab_flagged = tab_count >= 1
    paste_flagged = len(paste_events) > 0
    fullscreen_flagged = fullscreen_count >= 1

    if tab_flagged or paste_flagged or fullscreen_flagged:
        overall = "⚠️ Review Required"
    else:
        overall = "✅ Clean"

    return {
        "tab_switch_count": tab_count,
        "tab_flagged": tab_flagged,
        "paste_detected": paste_flagged,
        "paste_questions": paste_questions,
        "fullscreen_exit_count": fullscreen_count,
        "fullscreen_flagged": fullscreen_flagged,
        "auto_snapshot_count": len(auto_snapshots),
        "overall": overall
    }