import io
import os
import tempfile
import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from fpdf import FPDF

HEADER_LOGO = "assets/logo_square.png"
FOOTER_LOGO = "assets/logo_round.png"


def _sanitize(text):
    """
    Replaces common unicode characters that fall outside latin-1 range
    so fpdf2 (Helvetica) can encode them without crashing.
    """
    if not text:
        return ""
    text = str(text)
    replacements = {
        "\u2013": "-",     # en dash
        "\u2014": "--",    # em dash
        "\u2015": "--",    # horizontal bar
        "\u2018": "'",     # left single quote
        "\u2019": "'",     # right single quote
        "\u201a": ",",     # single low quote
        "\u201c": '"',     # left double quote
        "\u201d": '"',     # right double quote
        "\u201e": '"',     # double low quote
        "\u2022": "*",     # bullet
        "\u2023": "*",     # triangular bullet
        "\u2026": "...",   # ellipsis
        "\u2039": "<",     # single left angle quote
        "\u203a": ">",     # single right angle quote
        "\u00a0": " ",     # non-breaking space
        "\u200b": "",      # zero-width space
        "\u200c": "",      # zero-width non-joiner
        "\u200d": "",      # zero-width joiner
        "\u2192": "->",    # right arrow
        "\u2190": "<-",    # left arrow
        "\u2713": "✓".encode("latin-1", errors="replace").decode("latin-1"),
        "\u00e2\u0080\u0099": "'",  # mojibake apostrophe
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Final safety net: replace anything still unmappable
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_report(scores, answers, webcam_results=None):

    total_questions = len(answers)
    average_score = round(sum(scores) / len(scores), 2) if scores else 0

    if average_score >= 80:
        strength = "Strong technical understanding."
        weakness = "Minor improvements needed."
        band = "Strong"
    elif average_score >= 60:
        strength = "Good foundation."
        weakness = "Need more detailed answers."
        band = "Average"
    else:
        strength = "Willing to attempt questions."
        weakness = "Need stronger technical knowledge."
        band = "Weak"

    avg_confidence = 0
    if webcam_results:
        analysed = [r for r in webcam_results if r.get("analysed")]
        if analysed:
            avg_confidence = round(
                sum(r["confidence_score"] for r in analysed) / len(analysed), 1
            )

    if answers:
        avg_len = sum(len(a.split()) for a in answers) / len(answers)
        if avg_len >= 60:
            communication_score = 90
        elif avg_len >= 30:
            communication_score = 70
        elif avg_len >= 10:
            communication_score = 50
        else:
            communication_score = 30
    else:
        communication_score = 0

    return {
        "total_questions": total_questions,
        "average_score": average_score,
        "technical_score": average_score,
        "confidence_score": avg_confidence if avg_confidence else round(average_score * 0.85, 1),
        "communication_score": communication_score,
        "strength": strength,
        "weakness": weakness,
        "band": band
    }


def _bar_chart(scores):
    fig, ax = plt.subplots(figsize=(7, 3.5))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    x = [f"Q{i+1}" for i in range(len(scores))]
    colors = ["#4caf50" if s >= 80 else "#ff9800" if s >= 60 else "#f44336" for s in scores]
    bars = ax.bar(x, scores, color=colors, edgecolor="#333", width=0.5)

    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.5,
            str(score),
            ha="center", va="bottom",
            color="white", fontsize=10, fontweight="bold"
        )

    ax.set_ylim(0, 110)
    ax.set_ylabel("Score", color="white")
    ax.set_xlabel("Question", color="white")
    ax.set_title("Score Per Question", color="white", fontsize=13, fontweight="bold")
    ax.tick_params(colors="white")
    ax.spines[:].set_color("#444")

    green = mpatches.Patch(color="#4caf50", label="Strong (>=80)")
    orange = mpatches.Patch(color="#ff9800", label="Average (60-79)")
    red = mpatches.Patch(color="#f44336", label="Weak (<60)")
    ax.legend(handles=[green, orange, red], facecolor="#2a2a3e", labelcolor="white", fontsize=8)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf


def _radar_chart(technical, communication, confidence):
    categories = ["Technical", "Communication", "Confidence"]
    values = [technical, communication, confidence]

    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    values_plot = values + values[:1]

    fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    ax.plot(angles, values_plot, color="#7c4dff", linewidth=2)
    ax.fill(angles, values_plot, color="#7c4dff", alpha=0.3)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color="white", fontsize=11)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], color="#888", fontsize=7)
    ax.spines["polar"].set_color("#444")
    ax.grid(color="#444")
    ax.set_title("Performance Radar", color="white", fontsize=13,
                 fontweight="bold", pad=20)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_pdf(
    candidate_name, role, level, interview_type,
    scores, answers, questions, evaluation_results, report
):
    tmp_bar = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp_radar = tempfile.NamedTemporaryFile(suffix=".png", delete=False)

    try:
        bar_buf = _bar_chart(scores)
        tmp_bar.write(bar_buf.read())
        tmp_bar.flush()
        tmp_bar.close()

        radar_buf = _radar_chart(
            report["technical_score"],
            report["communication_score"],
            report["confidence_score"]
        )
        tmp_radar.write(radar_buf.read())
        tmp_radar.flush()
        tmp_radar.close()

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # ── Header ───────────────────────────────────────────────────────────
        pdf.set_fill_color(30, 30, 46)
        pdf.rect(0, 0, 210, 45, "F")

        # Logo
        if os.path.exists(HEADER_LOGO):
            pdf.image(HEADER_LOGO, x=10, y=7, w=24)

        # Title
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(38, 8)
        pdf.cell(0, 10, "AI Interview Coach", ln=True)

        # Subtitle
        pdf.set_font("Helvetica", "", 11)
        pdf.set_xy(38, 20)
        pdf.cell(0, 6, "Interview Performance Report", ln=True)

        # Candidate
        pdf.set_font("Helvetica", "", 11)
        pdf.set_xy(10, 33)
        pdf.cell(0, 6, _sanitize(f"Candidate: {candidate_name}"), ln=True)

        # Details
        pdf.set_font("Helvetica", "", 9)
        pdf.set_xy(10, 39)
        pdf.cell(
            0,
            5,
            _sanitize(
                f"Role: {role}  |  Level: {level}  |  Type: {interview_type}  |  "
                f"Date: {datetime.date.today().strftime('%d %B %Y')}"
            ),
            ln=True
        )

        pdf.set_y(52)
        pdf.set_text_color(0, 0, 0)

        # ── Summary ───────────────────────────────────────────────────────────
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(245, 245, 255)
        pdf.cell(0, 10, "Overall Summary", ln=True, fill=True)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 11)
        pdf.cell(60, 8, f"Questions Answered: {report['total_questions']}", ln=False)
        pdf.cell(60, 8, f"Average Score: {report['average_score']}/100", ln=False)
        pdf.cell(60, 8, f"Performance Band: {report['band']}", ln=True)
        pdf.ln(2)
        pdf.cell(60, 8, f"Technical Score: {report['technical_score']}/100", ln=False)
        pdf.cell(60, 8, f"Communication Score: {report['communication_score']}/100", ln=False)
        pdf.cell(60, 8, f"Confidence Score: {report['confidence_score']}/100", ln=True)
        pdf.ln(3)

        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(30, 7, "Strength:", ln=False)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, _sanitize(report["strength"]), ln=True)

        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(30, 7, "Weakness:", ln=False)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, _sanitize(report["weakness"]), ln=True)
        pdf.ln(4)

        # ── Charts ────────────────────────────────────────────────────────────
        if scores:
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_fill_color(245, 245, 255)
            pdf.cell(0, 10, "Score Per Question", ln=True, fill=True)
            pdf.ln(2)
            pdf.image(tmp_bar.name, x=15, w=170)
            pdf.ln(5)

        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(245, 245, 255)
        pdf.cell(0, 10, "Performance Radar", ln=True, fill=True)
        pdf.ln(2)
        pdf.image(tmp_radar.name, x=55, w=100)
        pdf.ln(5)

        # ── Per Question Breakdown ────────────────────────────────────────────
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(245, 245, 255)
        pdf.cell(0, 10, "Question-by-Question Breakdown", ln=True, fill=True)
        pdf.ln(3)

        for i, (q, a, s) in enumerate(zip(questions, answers, scores)):

            pdf.set_font("Helvetica", "B", 11)
            pdf.set_fill_color(230, 230, 245)
            q_text = _sanitize(f"Q{i+1}: {q[:100]}{'...' if len(q) > 100 else ''}")
            pdf.cell(0, 8, q_text, ln=True, fill=True)

            if s >= 80:
                pdf.set_text_color(56, 142, 60)
            elif s >= 60:
                pdf.set_text_color(230, 119, 0)
            else:
                pdf.set_text_color(211, 47, 47)

            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, f"Score: {s}/100", ln=True)
            pdf.set_text_color(0, 0, 0)

            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Your Answer:", ln=True)
            pdf.set_font("Helvetica", "", 9)
            a_text = _sanitize(a[:500] + ("..." if len(a) > 500 else ""))
            pdf.multi_cell(0, 5, a_text)

            if evaluation_results and i < len(evaluation_results):
                ev = evaluation_results[i]
                if ev and ev.get("feedback"):
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.cell(0, 6, "Feedback:", ln=True)
                    pdf.set_font("Helvetica", "", 9)
                    fb = _sanitize(str(ev["feedback"])[:400])
                    pdf.multi_cell(0, 5, fb)

                if ev and ev.get("ideal_answer"):
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.cell(0, 6, "Ideal Answer:", ln=True)
                    pdf.set_font("Helvetica", "", 9)
                    ia = _sanitize(str(ev["ideal_answer"])[:400])
                    pdf.multi_cell(0, 5, ia)

            pdf.ln(4)

        # ── Footer ────────────────────────────────────────────────────────────
        # ── Premium Branding Footer (Last Page) ───────────────────────────────

        # Leave some space after the last answer
        pdf.ln(10)

        # If we're too close to the bottom, move branding to a fresh page
        if pdf.get_y() > 215:
            pdf.add_page()

        # Divider
        pdf.set_draw_color(220, 220, 220)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())

        pdf.ln(8)

        # Heading
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(
            0,
            6,
            "Interview Practiced & Evaluated with",
            align="C",
            ln=True
        )

        pdf.ln(3)

        # Round Logo
        if os.path.exists(FOOTER_LOGO):
            x = (210 - 24) / 2
            pdf.image(FOOTER_LOGO, x=x, y=pdf.get_y(), w=24)

        pdf.ln(28)

        # Brand
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(
            0,
            6,
            "AI Interview Coach",
            align="C",
            ln=True
        )

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(
            0,
            5,
            "AI-Powered Mock Interview Platform",
            align="C"
        )

        result = pdf.output()
        return bytes(result) if isinstance(result, bytearray) else result

    finally:
        if os.path.exists(tmp_bar.name):
            os.unlink(tmp_bar.name)
        if os.path.exists(tmp_radar.name):
            os.unlink(tmp_radar.name)