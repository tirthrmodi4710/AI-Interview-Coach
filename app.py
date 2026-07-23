import streamlit as st
import json
import urllib.parse
from PIL import Image
from modules.session_manager import initialize_session, reset_interview
from modules.interview_engine import get_questions
from modules.ai_evaluator import evaluate_answer
from modules.report_generator import generate_report, generate_pdf, _bar_chart, _radar_chart
from modules.gemini_service import test_gemini, evaluate_with_gemini, generate_questions
from modules.voice_service import get_voice_component
from modules.webcam_service import analyze_pil_image
from modules.db_service import initialize_db, save_interview, get_user_interviews, delete_interview
from modules.auth_service import register_user, login_user
from modules.proctoring_service import get_interview_shell, get_integrity_summary
import base64
from PIL import Image

def load_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

page_icon = Image.open("assets/logo_square.png")

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon=page_icon,
    layout="wide"
)

# ── Development Configuration ──────────────────────────────────────────
DEV_MODE = False

# ── Global CSS (Premium Enterprise Design System) ───────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            
/* ===== Force Light Theme ===== */

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main,
section[data-testid="stMain"],
div[data-testid="stAppViewBlockContainer"] {
    background: #F5F7FA !important;
}

/* ── Reset & Base ───────────────────────────────────────────────────────────── */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html,
body {
    background: #F5F7FA !important;
    color: #111827;
    font-family: 'Inter', sans-serif;
}

.stApp{
    background:#F5F7FA !important;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container{
    max-width:1280px !important;
    padding:2rem !important;
    background:transparent !important;
}

/* ── Scrollbar ────────────────────────────────────────────────────────────────── */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: #F1F5F9;
    border-radius: 3px;
}

::-webkit-scrollbar-thumb {
    background: #2563EB;
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: #1E40AF;
}

/* ── Animations ───────────────────────────────────────────────────────────────── */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes countUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.3s ease-out;
}

.slide-in {
    animation: slideIn 0.3s ease-out;
}

.scale-in {
    animation: scaleIn 0.25s ease-out;
}

.count-up {
    animation: countUp 0.6s ease-out;
}

/* ── Typography ───────────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    color: #111827;
    font-weight: 700;
    letter-spacing: -0.02em;
}

h1 { font-size: 2.25rem; line-height: 1.2; }
h2 { font-size: 1.75rem; line-height: 1.3; }
h3 { font-size: 1.25rem; line-height: 1.4; }
h4 { font-size: 1rem; line-height: 1.5; }

/* Normal page text */
p,
li,
span {
    color: #6B7280;
    line-height: 1.6;
}

/* ── Force white text inside ALL buttons and tabs ───────────────────────── */

button,
button *,
button p,
button span,
button div,
button[data-baseweb="tab"],
button[data-baseweb="tab"] *,
button[data-baseweb="tab"] p,
button[data-baseweb="tab"] span,
button[data-baseweb="tab"] div,
button[data-baseweb="tab"] [data-testid="stMarkdownContainer"],
button[data-baseweb="tab"] [data-testid="stMarkdownContainer"] *,
.stButton button,
.stButton button *,
.stDownloadButton button,
.stDownloadButton button * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Download button label */
.stDownloadButton button p,
.stDownloadButton button span,
.stDownloadButton button div {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* ── Blue background for Streamlit tabs ───────────────────────────────── */

button[data-baseweb="tab"] {
    background: #2563EB !important;
    border: none !important;
    border-radius: 12px !important;
}

button[data-baseweb="tab"]:hover {
    background: #1E40AF !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: #1E40AF !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────────────── */
.stButton > button {
    background: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 0.625rem 1.5rem;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.875rem;
    letter-spacing: 0.01em;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 3px rgba(37, 99, 235, 0.12);
    position: relative;
    overflow: hidden;
    cursor: pointer;
}

.stButton > button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
    opacity: 0;
    transition: opacity 0.2s ease;
}

.stButton > button:hover {
    background: #1E40AF;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
}

.stButton > button:hover::before {
    opacity: 1;
}

.stButton > button:active {
    transform: translateY(0px);
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.15);
}

.stButton > button:focus-visible {
    outline: 2px solid #2563EB;
    outline-offset: 2px;
}

/* Download Button */
    .stDownloadButton > button {
        background: #2563EB;
        color: #FFFFFF !important;
        border: none;
        border-radius: 12px;
        padding: 0.625rem 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.875rem;
        letter-spacing: 0.01em;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(37,99,235,.12);
    }

    .stDownloadButton > button:hover {
        background: #1E40AF;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(37,99,235,.25);
    }

    .stDownloadButton > button p,
    .stDownloadButton > button span,
    .stDownloadButton > button div,
    .stDownloadButton > button * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

/* ── Streamlit Tabs (BaseWeb) ───────────────────────────── */

button[data-baseweb="tab"] {
    background: #2563EB !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    border: none !important;
    font-weight: 600 !important;
    transition: all .2s ease !important;
}

button[data-baseweb="tab"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

button[data-baseweb="tab"]:hover {
    background: #1E40AF !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: #1E40AF !important;
    color: #FFFFFF !important;
}

/* ── Inputs ──────────────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #FFFFFF;
    border: 2px solid #E5E7EB;
    border-radius: 12px;
    padding: 0.75rem 1rem;
    color: #111827;
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #2563EB;
    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1), 0 1px 2px rgba(0,0,0,0.04);
    outline: none;
}

.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #9CA3AF;
}

.stTextInput > label,
.stTextArea > label {
    color: #374151;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

/* ── Select Box ──────────────────────────────────────────────────────────────── */
.stSelectbox > div > div {
    background: #FFFFFF;
    border: 2px solid #E5E7EB;
    border-radius: 12px;
    color: #111827;
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.stSelectbox > div > div:hover {
    border-color: #2563EB;
}

.stSelectbox > div > div:focus-within {
    border-color: #2563EB;
    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
}

.stSelectbox > label {
    color: #374151;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

/* ── Toggle ──────────────────────────────────────────────────────────────────── */
.stToggle > label {
    color: #374151;
    font-weight: 500;
    font-size: 0.875rem;
}

.stToggle > div[data-baseweb="toggle"] {
    transition: all 0.2s ease;
}

/* ── Tabs ────────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #F1F5F9;
    border-radius: 14px;
    padding: 4px;
    gap: 4px;
    border: none;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #6B7280;
    font-weight: 500;
    font-size: 0.875rem;
    border-radius: 10px;
    padding: 0.5rem 1.25rem;
    transition: all 0.2s ease;
    border: none;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #111827;
    background: rgba(255,255,255,0.5);
}

.stTabs [aria-selected="true"] {
    background: #FFFFFF;
    color: #2563EB;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* ── Alerts ──────────────────────────────────────────────────────────────────── */
[data-testid="stInfo"] {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 12px;
    color: #1E40AF;
    padding: 1rem 1.25rem;
    font-size: 0.875rem;
}

[data-testid="stSuccess"] {
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
    border-radius: 12px;
    color: #065F46;
    padding: 1rem 1.25rem;
    font-size: 0.875rem;
}

[data-testid="stWarning"] {
    background: #FFFBEB;
    border: 1px solid #FCD34D;
    border-radius: 12px;
    color: #92400E;
    padding: 1rem 1.25rem;
    font-size: 0.875rem;
}

[data-testid="stError"] {
    background: #FEF2F2;
    border: 1px solid #FCA5A5;
    border-radius: 12px;
    color: #991B1B;
    padding: 1rem 1.25rem;
    font-size: 0.875rem;
}

/* ── Expanders ───────────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: #FFFFFF;
    border: 2px solid #E5E7EB;
    border-radius: 12px;
    color: #111827;
    font-weight: 500;
    padding: 0.75rem 1rem;
    transition: all 0.2s ease;
}

.streamlit-expanderHeader:hover {
    border-color: #2563EB;
    background: #F8FAFC;
}

.streamlit-expanderContent {
    background: #FFFFFF;
    border: 2px solid #E5E7EB;
    border-top: none;
    border-radius: 0 0 12px 12px;
    padding: 1rem 1.25rem;
}

/* ── Metric Cards ────────────────────────────────────────────────────────────── */
[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: #111827;
}

[data-testid="stMetricLabel"] {
    color: #6B7280;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

[data-testid="stMetricDelta"] {
    font-size: 0.75rem;
}

/* ── Progress Bar ────────────────────────────────────────────────────────────── */
.stProgress > div > div {
    background: linear-gradient(90deg, #2563EB, #60A5FA);
    border-radius: 99px;
    height: 6px;
}

.stProgress > div {
    background: #E5E7EB;
    border-radius: 99px;
    height: 6px;
}

/* ── Camera ──────────────────────────────────────────────────────────────────── */
[data-testid="stCameraInput"] {
    background: #FFFFFF;
    border: 2px solid #E5E7EB;
    border-radius: 12px;
    overflow: hidden;
}

/* ── Spinner ─────────────────────────────────────────────────────────────────── */
.stSpinner > div {
    border-top-color: #2563EB !important;
    border-width: 3px !important;
}

/* ── Caption ─────────────────────────────────────────────────────────────────── */
.stCaption {
    color: #6B7280 !important;
    font-size: 0.75rem;
}

/* ── Enterprise Card Components ────────────────────────────────────────────── */
.enterprise-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 1.75rem;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.enterprise-card:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border-color: #D1D5DB;
}

.enterprise-card-accent {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 1.75rem;
    border-top: 4px solid #2563EB;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.enterprise-card-accent:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.enterprise-card-success {
    background: #FFFFFF;
    border: 1px solid #A7F3D0;
    border-radius: 16px;
    padding: 1.75rem;
    border-top: 4px solid #10B981;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.enterprise-card-success:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.enterprise-card-danger {
    background: #FFFFFF;
    border: 1px solid #FCA5A5;
    border-radius: 16px;
    padding: 1.75rem;
    border-top: 4px solid #EF4444;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.enterprise-card-danger:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.enterprise-card-premium {
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1px solid #E5E7EB;
    border-radius: 20px;
    padding: 2rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    position: relative;
    overflow: hidden;
}

.enterprise-card-premium::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #2563EB, #60A5FA, #2563EB);
    background-size: 200% 100%;
    animation: shimmer 3s ease-in-out infinite;
}

.enterprise-card-premium:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.08);
    border-color: #D1D5DB;
}

/* ── Dashboard KPI Cards ────────────────────────────────────────────────────── */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 1.5rem 1.75rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    position: relative;
    overflow: hidden;
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    border-color: #D1D5DB;
}

.kpi-card .kpi-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.kpi-card .kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #111827;
    margin: 0.25rem 0 0.125rem;
    letter-spacing: -0.02em;
}

.kpi-card .kpi-label {
    font-size: 0.75rem;
    color: #6B7280;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.kpi-card .kpi-trend {
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 0.25rem;
    padding: 0.125rem 0.5rem;
    border-radius: 99px;
    display: inline-block;
}

.kpi-card .kpi-trend.up {
    color: #10B981;
    background: #ECFDF5;
}

.kpi-card .kpi-trend.down {
    color: #EF4444;
    background: #FEF2F2;
}

.kpi-card .kpi-trend.neutral {
    color: #6B7280;
    background: #F1F5F9;
}

.kpi-card.primary {
    border-top: 4px solid #2563EB;
}

.kpi-card.success {
    border-top: 4px solid #10B981;
}

.kpi-card.warning {
    border-top: 4px solid #F59E0B;
}

.kpi-card.danger {
    border-top: 4px solid #EF4444;
}

.kpi-card.purple {
    border-top: 4px solid #8B5CF6;
}

/* ── Section Headers ────────────────────────────────────────────────────────── */
.section-header {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #2563EB;
    margin-bottom: 0.75rem;
}

.section-header-light {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6B7280;
    margin-bottom: 0.75rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 0.25rem;
    letter-spacing: -0.02em;
}

.section-subtitle {
    font-size: 0.875rem;
    color: #6B7280;
    margin-bottom: 1.5rem;
}

/* ── Band Colors ────────────────────────────────────────────────────────────── */
.band-strong {
    color: #10B981;
    font-weight: 600;
}

.band-average {
    color: #F59E0B;
    font-weight: 600;
}

.band-weak {
    color: #EF4444;
    font-weight: 600;
}

/* ── Page Header ────────────────────────────────────────────────────────────── */
.page-header {
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1px solid #E5E7EB;
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.page-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #2563EB, #60A5FA, #2563EB);
    background-size: 200% 100%;
    animation: shimmer 3s ease-in-out infinite;
}

.page-header h1 {
    font-size: 2rem;
    font-weight: 800;
    color: #111827;
    margin: 0;
    letter-spacing: -0.02em;
}

.page-header p {
    color: #6B7280;
    margin: 0.25rem 0 0 0;
    font-size: 0.95rem;
}

/* ── Setup Configuration Card ───────────────────────────────────────────────── */
.setup-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 20px;
    padding: 2rem 2.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.setup-card:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.setup-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-top: 1rem;
}

.setup-field-group {
    background: #F8FAFC;
    border: 1px solid #F1F5F9;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    transition: all 0.2s ease;
}

.setup-field-group:hover {
    border-color: #E5E7EB;
    background: #FFFFFF;
}

.setup-field-group .field-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #6B7280;
    margin-bottom: 0.25rem;
}

.setup-field-group .field-value {
    font-size: 0.9rem;
    font-weight: 500;
    color: #111827;
}

/* ── Navbar ──────────────────────────────────────────────────────────────────── */
.enterprise-navbar {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 0.75rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    margin-bottom: 1.5rem;
    transition: all 0.2s ease;
}

.enterprise-navbar:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.enterprise-brand {
    font-size: 1.25rem;
    font-weight: 800;
    color: #111827;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.enterprise-brand span {
    color: #2563EB;
}

.enterprise-user {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.875rem;
    color: #374151;
    font-weight: 500;
    background: #F1F5F9;
    padding: 0.375rem 1rem;
    border-radius: 99px;
}

.enterprise-user-avatar {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #2563EB, #60A5FA);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 0.875rem;
}

/* ───────── Welcome Banner ───────── */

.welcome-banner{
    background: linear-gradient(135deg,#2563EB 0%,#3B82F6 100%);
    border-radius:20px;
    padding:32px 38px;
    margin-bottom:32px;
    position:relative;
    overflow:hidden;
    box-shadow:0 12px 35px rgba(37,99,235,.18);
}

.welcome-banner::before{
    content:"";
    position:absolute;
    inset:0;
    background:linear-gradient(
        120deg,
        rgba(255,255,255,.08),
        transparent 45%
    );
}

.welcome-badge{
    display:inline-block;
    background:rgba(255,255,255,.18);
    color:#fff;
    font-size:12px;
    font-weight:600;
    letter-spacing:.08em;
    text-transform:uppercase;
    padding:6px 12px;
    border-radius:999px;
    margin-bottom:18px;
    backdrop-filter:blur(8px);
}

.welcome-banner h1,
.welcome-banner h1 *,
.welcome-banner [data-testid="stMarkdownContainer"] h1 {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 10px;
    position: relative;
    z-index: 2;
}

.welcome-banner p,
.welcome-banner [data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,.92) !important;
    -webkit-text-fill-color: rgba(255,255,255,.92) !important;
    opacity: 1 !important;
    font-size: 1rem;
    line-height: 1.7;
    max-width: 720px;
    margin: 0;
    position: relative;
    z-index: 2;
}

/* ── Report Dashboard Components ────────────────────────────────────────────── */
.report-header {
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1px solid #E5E7EB;
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.report-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #10B981, #34D399, #10B981);
    background-size: 200% 100%;
    animation: shimmer 3s ease-in-out infinite;
}

.report-header h1 {
    font-size: 1.75rem;
    font-weight: 800;
    color: #111827;
    margin: 0;
    letter-spacing: -0.02em;
}

.report-header .report-meta {
    display: flex;
    gap: 1.5rem;
    margin-top: 0.5rem;
    flex-wrap: wrap;
}

.report-header .report-meta-item {
    font-size: 0.875rem;
    color: #6B7280;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.report-header .report-meta-item strong {
    color: #111827;
    font-weight: 600;
}

.report-band-badge {
    display: inline-block;
    padding: 0.25rem 1rem;
    border-radius: 99px;
    font-weight: 700;
    font-size: 0.875rem;
}

.report-band-badge.strong {
    background: #ECFDF5;
    color: #10B981;
}

.report-band-badge.average {
    background: #FFFBEB;
    color: #F59E0B;
}

.report-band-badge.weak {
    background: #FEF2F2;
    color: #EF4444;
}

/* ── AI Feedback Card ────────────────────────────────────────────────────────── */
.ai-feedback-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.ai-feedback-card:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.ai-feedback-card .feedback-icon {
    font-size: 1.5rem;
    margin-right: 0.75rem;
}

.ai-feedback-card .feedback-title {
    font-weight: 600;
    color: #111827;
    font-size: 0.875rem;
}

.ai-feedback-card .feedback-text {
    color: #6B7280;
    font-size: 0.9rem;
    line-height: 1.6;
    margin-top: 0.5rem;
}

/* ── Strength/Weakness Cards ────────────────────────────────────────────────── */
.strength-card {
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    border-left: 4px solid #10B981;
}

.weakness-card {
    background: #FEF2F2;
    border: 1px solid #FCA5A5;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    border-left: 4px solid #EF4444;
}

/* ── Responsive ──────────────────────────────────────────────────────────────── */
@media (max-width: 1024px) {
    .setup-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .report-header .report-meta {
        gap: 1rem;
    }
}

@media (max-width: 768px) {
    .block-container {
        padding: 1rem !important;
    }
    
    .page-header {
        padding: 1.5rem;
    }
    
    .page-header h1 {
        font-size: 1.5rem;
    }
    
    .enterprise-navbar {
        flex-direction: column;
        gap: 0.75rem;
        padding: 1rem;
    }
    
    .welcome-banner {
        padding: 1.5rem;
    }
    
    .welcome-banner h1 {
        font-size: 1.25rem;
    }
    
    .setup-card {
        padding: 1.25rem;
    }
    
    .report-header {
        padding: 1.5rem;
    }
    
    .report-header h1 {
        font-size: 1.25rem;
    }
    
    .kpi-card .kpi-value {
        font-size: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 0.75rem;
        padding: 0.375rem 0.75rem;
    }
    
    .enterprise-card-premium {
        padding: 1.5rem;
    }
}

@media (max-width: 480px) {
    .block-container {
        padding: 0.75rem !important;
    }
    
    .page-header {
        padding: 1rem;
    }
    
    .page-header h1 {
        font-size: 1.25rem;
    }
    
    .setup-card {
        padding: 1rem;
    }
    
    .report-header {
        padding: 1rem;
    }
    
    .report-header .report-meta {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .kpi-card {
        padding: 1rem 1.25rem;
    }
    
    .kpi-card .kpi-value {
        font-size: 1.25rem;
    }
    
    .ai-feedback-card {
        padding: 1rem 1.25rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ── Session Init ──────────────────────────────────────────────────────────────
initialize_session()

# ── Auth Gate ─────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:

    st.markdown("""
    <style>
    /* ── Auth Page Override ──────────────────────────────────────────────────── */
    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%) !important;
    }
    
    .block-container {
        max-width: 480px !important;
        padding: 2rem 1.5rem !important;
        display: flex;
        align-items: center;
        min-height: 100vh;
    }
    
    .auth-card {
        padding: 0;
    }

    .auth-logo {
        padding: 1.5rem 2rem 1rem;
        text-align: center;
    }

    .auth-content {
        padding: 0 2rem 2rem;
    }

    .auth-logo-image {
        width: 210%;
        max-width: 560px;
        height: auto;
        display: block;
        margin: 0 auto 18px auto;
    }
    
    .auth-logo p {
        color: #6B7280;
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
    
    .auth-label {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #2563EB;
        margin-bottom: 0.75rem;
    }
    
    .auth-footer {
        text-align: center;
        margin-top: 1.5rem;
        font-size: 0.75rem;
        color: #9CA3AF;
    }
    
    .auth-footer a {
        color: #2563EB;
        text-decoration: none;
        font-weight: 500;
    }
    
    .auth-footer a:hover {
        text-decoration: underline;
    }
    
    .stTextInput > label {
        display: none !important;
    }
    
    .stTextInput > div > div > input {
        padding: 0.875rem 1rem !important;
        font-size: 0.875rem !important;
        border-radius: 12px !important;
    }
    
    .stButton > button {
        width: 100% !important;
        padding: 0.875rem !important;
        font-size: 0.875rem !important;
        border-radius: 12px !important;
        margin-top: 0.5rem;
    }

    /* Force ALL Streamlit button text to white */
    .stButton > button,
    .stButton > button *,
    button[data-testid^="stBaseButton"],
    button[data-testid^="stBaseButton"] *,
    button[data-testid="stBaseButton-primary"],
    button[data-testid="stBaseButton-primary"] *,
    button[data-testid="stBaseButton-secondary"],
    button[data-testid="stBaseButton-secondary"] *,
    button[kind="primary"],
    button[kind="primary"] *,
    button[kind="secondary"],
    button[kind="secondary"] * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        opacity: 1 !important;
    }

    .stButton > button [data-testid="stMarkdownContainer"] p,
    button[data-testid^="stBaseButton"] [data-testid="stMarkdownContainer"] p,
    button[data-testid="stBaseButton-primary"] [data-testid="stMarkdownContainer"] p,
    button[data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        margin: 0 !important;
        opacity: 1 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # Auth Card
    logo_base64 = load_base64_image("assets/logo_rectangle.png")

    st.markdown(f"""
    <div class="auth-card">
        <div class="auth-logo">
            <img
                src="data:image/png;base64,{logo_base64}"
                class="auth-logo-image"
            />
            <p>--AI Powered Practice Interview--</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    auth_tab, register_tab = st.tabs(["Sign In", "Create Account"])

    with auth_tab:
        st.markdown("<div class='auth-label'>Welcome back</div>", unsafe_allow_html=True)
        login_email = st.text_input("Email Address", key="login_email", placeholder="you@example.com")
        login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        if st.button("Sign In →", key="login_btn", use_container_width=True):
            success, result = login_user(login_email, login_password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user = result
                st.session_state.candidate_name = result["name"]
                st.rerun()
            else:
                st.error(result)

    with register_tab:
        st.markdown("<div class='auth-label'>Create your account</div>", unsafe_allow_html=True)
        reg_name = st.text_input("Full Name", key="reg_name", placeholder="Enter your full name")
        reg_email = st.text_input("Email Address", key="reg_email", placeholder="you@example.com")
        reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Minimum 6 characters")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Repeat your password")
        if st.button("Create Account →", key="register_btn", use_container_width=True):
            if reg_password != reg_confirm:
                st.error("Passwords do not match.")
            else:
                success, message = register_user(reg_name, reg_email, reg_password)
                if success:
                    login_success, login_result = login_user(reg_email, reg_password)
                    if login_success:
                        st.session_state.logged_in = True
                        st.session_state.user = login_result
                        st.session_state.candidate_name = login_result["name"]
                        st.rerun()
                    else:
                        st.success("Account created! Please log in.")
                else:
                    st.error(message)

    st.markdown("""
        <div class="auth-footer">
            By continuing, you agree to our <a href="#">Terms of Service</a>. <br>
            🔒 Secure authentication powered by Supabase..
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.stop()

# ── Authenticated App ─────────────────────────────────────────────────────────
user = st.session_state.user

# ═════════════════════════════════════════════════════════════════════════════
# ACTIVE INTERVIEW — Full page Mettl-style shell
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.interview_started and not st.session_state.interview_completed:

    idx = st.session_state.current_question_index
    total_questions = len(st.session_state.questions)

    # ── Read navigation + proctoring events from URL ──────────────────────────
    nav_to = None
    nav_answer = None
    try:
        nav_to_raw = st.query_params.get("nav_to", "")
        nav_answer_raw = st.query_params.get("nav_answer", "")
        pe_raw = st.query_params.get("proctor_events", "")

        if nav_to_raw != "":
            nav_to = int(nav_to_raw)
        if nav_answer_raw:
            nav_answer = urllib.parse.unquote(nav_answer_raw)
        if pe_raw:
            events = json.loads(urllib.parse.unquote(pe_raw))
            for ev in events:
                if ev not in st.session_state.proctoring_log:
                    st.session_state.proctoring_log.append(ev)

        st.query_params.clear()
    except Exception:
        pass

    # ── Process navigation ────────────────────────────────────────────────────
    if nav_to is not None:
        # Save the answer for the current question
        if nav_answer:
            while len(st.session_state.answers) <= idx:
                st.session_state.answers.append("")
            st.session_state.answers[idx] = nav_answer

        if nav_to == -1:
            # Submit interview
            with st.spinner("Evaluating all your answers..."):
                scores = []
                evaluation_results = []
                evaluation_mode = st.session_state.get("_evaluation_mode", "Local")
                for q, a in zip(st.session_state.questions, st.session_state.answers):
                    if evaluation_mode == "Local":
                        result = evaluate_answer(q, a)
                    else:
                        try:
                            result = evaluate_with_gemini(q, a)
                        except Exception:
                            result = evaluate_answer(q, a)
                    scores.append(result["score"])
                    evaluation_results.append(result)
            st.session_state.scores = scores
            st.session_state.evaluation_results = evaluation_results
            st.session_state.interview_completed = True
            st.session_state.interview_started = False
            st.rerun()
        else:
            st.session_state.current_question_index = nav_to
            st.rerun()

    # ── Calculate duration ────────────────────────────────────────────────────
    duration_seconds = total_questions * 6 * 60  # 6 minutes per question

    # ── Render full-page interview shell ──────────────────────────────────────
    # Hide only Streamlit chrome, not the content area
    st.markdown("""
    <style>
    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stSidebarNav"] { visibility: hidden !important; display: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    section[data-testid="stMain"] > div:first-child { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.components.v1.html(
        get_interview_shell(
            total_questions=total_questions,
            duration_seconds=duration_seconds,
            question_index=idx,
            questions=st.session_state.questions,
            answers=st.session_state.answers,
            webcam_enabled=st.session_state.get("_webcam_enabled", True),
            answer_mode=st.session_state.get("answer_mode", "Type")
        ),
        height=900,
        scrolling=True
    )

    # Hidden NAV_SYNC button — clicked by JS to trigger rerun
    if st.button("NAV_SYNC", key="nav_sync_btn"):
        pass

    st.stop()

# ── Top bar (shown outside interview) ────────────────────────────────────────

# Navbar
st.markdown(f"""
<div class="enterprise-navbar fade-in">
    <div class="enterprise-brand">
        🎯 AI Interview <span>Coach</span>
    </div>
    <div style="display:flex; align-items:center; gap:1rem;">
        <span style="color:#6B7280; font-size:0.875rem;">Sharpen your answers. Analyse your presence. Land the role.</span>
        <div class="enterprise-user">
            <div class="enterprise-user-avatar">{user['name'][0].upper()}</div>
            {user['name']}
        </div>
        <div style="width:1px; height:32px; background:#E5E7EB;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("Logout", key="logout_btn"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

if DEV_MODE:
    interview_tab, history_tab, test_tab = st.tabs([
        "🎤  Interview",
        "📋  History",
        "🛠  Dev Tools"
    ])
else:
    interview_tab, history_tab = st.tabs([
        "🎤  Interview",
        "📋  History"
    ])

# ═════════════════════════════════════════════════════════════════════════════
# INTERVIEW TAB — Setup screen (PREMIUM REDESIGN)
# ═════════════════════════════════════════════════════════════════════════════
with interview_tab:

    if not st.session_state.interview_completed:

        # Welcome Banner
        st.markdown(f"""
        <div class="welcome-banner fade-in">
            <div class="welcome-badge">AI Interview Coach</div>
            <h1>Welcome.. {user['name']}</h1>
            <p>
                Prepare for your next interview with AI-powered practice sessions.
                Get real-time feedback and actionable insights.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ── Premium Setup Configuration ──────────────────────────────────────
        st.markdown("""
        <div class="section-header">Interview Configuration</div>
        <div class="section-title">Set Up Your Practice Session</div>
        <div class="section-subtitle">Customize your interview experience with the settings below</div>
        """, unsafe_allow_html=True)

        # Main Setup Card
        st.markdown('<div class="setup-card fade-in">', unsafe_allow_html=True)

        # Candidate Name - Full width
        setup_col = st.columns([2, 1])[0]
        with setup_col:
            candidate_name = st.text_input(
                "Candidate Name",
                placeholder="Enter your full name",
                value=st.session_state.get("candidate_name", user["name"])
            )
            st.session_state.candidate_name = candidate_name

        # Configuration Grid
        st.markdown('<div class="setup-grid">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="setup-field-group">', unsafe_allow_html=True)
            st.markdown('<div class="field-label">Job Role</div>', unsafe_allow_html=True)
            role = st.selectbox("", ["Python Developer", "Java Developer", "Data Analyst", "Frontend Developer"], label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="setup-field-group">', unsafe_allow_html=True)
            st.markdown('<div class="field-label">Interview Type</div>', unsafe_allow_html=True)
            interview_type = st.selectbox("", ["Technical", "HR", "Mixed"], label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="setup-field-group">', unsafe_allow_html=True)
            st.markdown('<div class="field-label">Question Source</div>', unsafe_allow_html=True)
            question_source = st.selectbox("", ["Static Bank", "AI Generated"], label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="setup-field-group">', unsafe_allow_html=True)
            st.markdown('<div class="field-label">Experience Level</div>', unsafe_allow_html=True)
            level = st.selectbox("", ["Beginner", "Intermediate", "Advanced"], label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="setup-field-group">', unsafe_allow_html=True)
            st.markdown('<div class="field-label">Evaluation Mode</div>', unsafe_allow_html=True)
            evaluation_mode = st.selectbox("", ["Local", "AI"], label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="setup-field-group">', unsafe_allow_html=True)
            st.markdown('<div class="field-label">Answer Mode</div>', unsafe_allow_html=True)
            answer_mode = st.selectbox("", ["Type", "Voice"], label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # End setup-grid

        # Additional Settings - Full width
        st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)

        if question_source == "AI Generated":
            col_q = st.columns([1, 3])[0]
            with col_q:
                st.markdown('<div class="setup-field-group">', unsafe_allow_html=True)
                st.markdown('<div class="field-label">Number of Questions</div>', unsafe_allow_html=True)
                num_questions = st.selectbox("", [5, 10, 15], label_visibility="collapsed")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            num_questions = 5

        webcam_enabled = st.toggle(
            "Enable Webcam Monitoring",
            value=True,
            help="Shows live webcam feed and auto-captures snapshots every 2 minutes during the interview."
        )

        st.markdown('</div>', unsafe_allow_html=True)  # End additional settings

        st.markdown('</div>', unsafe_allow_html=True)  # End setup-card

        # ── Interview Duration & Info ──────────────────────────────────────
        st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
        duration_mins = (num_questions if question_source == "AI Generated" else 5) * 6

        info_col1, info_col2 = st.columns([3, 1])
        with info_col1:
            st.markdown(f"""
            <div class="enterprise-card" style="border-left: 4px solid #2563EB;">
                <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                    <div>
                        <span style="font-size: 1.5rem;">⏱</span>
                    </div>
                    <div>
                        <div style="font-weight: 600; color: #111827;">Interview Duration</div>
                        <div style="color: #6B7280; font-size: 0.875rem;">
                            {duration_mins} minutes · {(num_questions if question_source == "AI Generated" else 5)} questions × 6 minutes each
                        </div>
                    </div>
                    <div style="margin-left: auto;">
                        <span style="background: #EFF6FF; color: #1E40AF; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 600;">
                            Auto-submit on timeout
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with info_col2:
            st.markdown(f"""
            <div class="enterprise-card" style="text-align: center; border-left: 4px solid #8B5CF6;">
                <div style="font-size: 1.75rem; font-weight: 700; color: #111827;">{duration_mins}</div>
                <div style="font-size: 0.75rem; color: #6B7280;">Total Minutes</div>
            </div>
            """, unsafe_allow_html=True)

        st.caption("📋 The interview will open in fullscreen mode. Do not exit fullscreen or switch tabs — violations are recorded.")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Start Button ──────────────────────────────────────────────────────
        st.markdown('<div style="margin-top: 2rem; display: flex; justify-content: center;">', unsafe_allow_html=True)
        if st.button("🚀 Start Interview", use_container_width=False):
            if question_source == "Static Bank":
                questions = get_questions(role, level)
            else:
                with st.spinner("Generating questions with AI..."):
                    try:
                        questions = generate_questions(role, level, interview_type, num_questions)
                    except Exception:
                        st.warning("Gemini AI is temporarily unavailable. Using the static question bank instead.")
                        questions = get_questions(role, level)

            st.session_state.answer_mode = answer_mode
            st.session_state.interview_started = True
            st.session_state.interview_completed = False
            st.session_state._interview_saved = False
            st.session_state.questions = questions
            st.session_state.current_question_index = 0
            st.session_state.answers = []
            st.session_state.scores = []
            st.session_state.evaluation_results = []
            st.session_state.webcam_results = []
            st.session_state.proctoring_log = []
            st.session_state.auto_snapshots = []
            st.session_state._role = role
            st.session_state._level = level
            st.session_state._interview_type = interview_type
            st.session_state._evaluation_mode = evaluation_mode
            st.session_state._question_source = question_source
            st.session_state._answer_mode = answer_mode
            st.session_state._webcam_enabled = webcam_enabled
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Interview Complete Report ──────────────────────────────────────────────
    if st.session_state.interview_completed:

        role            = st.session_state.get("_role", "Python Developer")
        level           = st.session_state.get("_level", "Beginner")
        interview_type  = st.session_state.get("_interview_type", "Technical")
        evaluation_mode = st.session_state.get("_evaluation_mode", "Local")
        question_source = st.session_state.get("_question_source", "Static Bank")

        webcam_results = st.session_state.get("webcam_results", [])
        report = generate_report(st.session_state.scores, st.session_state.answers, webcam_results)
        integrity = get_integrity_summary(st.session_state.get("proctoring_log", []))

        if not st.session_state.get("_interview_saved", False):
            save_interview(user["id"], {
                "candidate_name": st.session_state.get("candidate_name", user["name"]),
                "role": role, "level": level, "interview_type": interview_type,
                "evaluation_mode": evaluation_mode, "question_source": question_source,
                "total_questions": report["total_questions"],
                "average_score": report["average_score"],
                "technical_score": report["technical_score"],
                "communication_score": report["communication_score"],
                "confidence_score": report["confidence_score"],
                "band": report["band"],
                "scores": st.session_state.scores,
                "questions": st.session_state.questions,
                "answers": st.session_state.answers,
                "evaluation_results": st.session_state.get("evaluation_results", [])
            })
            st.session_state._interview_saved = True

        name_display = st.session_state.get("candidate_name", user["name"]) or user["name"]
        band_class = f"band-{report['band'].lower()}"
        band_badge_class = "strong" if report['band'].lower() == "strong" else "average" if report['band'].lower() == "average" else "weak"

        # ── Premium Report Dashboard ──────────────────────────────────────────
        st.markdown(f"""
        <div class="report-header fade-in">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <div class="section-header">Interview Complete</div>
                    <h1>Performance Report</h1>
                    <div class="report-meta">
                        <span class="report-meta-item">👤 <strong>{name_display}</strong></span>
                        <span class="report-meta-item">💼 <strong>{role}</strong></span>
                        <span class="report-meta-item">📊 <strong>{level}</strong></span>
                        <span class="report-meta-item">📝 <strong>{interview_type}</strong></span>
                    </div>
                </div>
                <div>
                    <span class="report-band-badge {band_badge_class}">{report['band']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── KPI Dashboard ─────────────────────────────────────────────────────
        st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)

        kpi_cols = st.columns(4)
        kpi_data = [
            {"icon": "📊", "value": f"{report['average_score']}/100", "label": "Overall Score", "class": "primary", "trend": "up", "trend_text": "Average"},
            {"icon": "⚡", "value": f"{report['technical_score']}/100", "label": "Technical", "class": "purple", "trend": "up", "trend_text": "Skill"},
            {"icon": "💬", "value": f"{report['communication_score']}/100", "label": "Communication", "class": "success", "trend": "up", "trend_text": "Clarity"},
            {"icon": "🎯", "value": f"{report['confidence_score']}/100", "label": "Confidence", "class": "warning", "trend": "up", "trend_text": "Delivery"}
        ]

        for i, (col, data) in enumerate(zip(kpi_cols, kpi_data)):
            with col:
                st.markdown(f"""
                <div class="kpi-card {data['class']} count-up" style="animation-delay: {i * 0.1}s;">
                    <div class="kpi-icon">{data['icon']}</div>
                    <div class="kpi-value">{data['value']}</div>
                    <div class="kpi-label">{data['label']}</div>
                    <span class="kpi-trend {data['trend']}">{data['trend_text']}</span>
                </div>
                """, unsafe_allow_html=True)

        # ── Strengths & Weaknesses ────────────────────────────────────────────
        st.markdown('<div class="section-header" style="margin-top: 1.5rem;">AI Analysis</div>', unsafe_allow_html=True)

        sw_col1, sw_col2 = st.columns(2)

        with sw_col1:
            st.markdown(f"""
            <div class="strength-card fade-in">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.25rem;">💪</span>
                    <span style="font-weight: 600; color: #065F46;">Strengths</span>
                </div>
                <p style="color: #065F46; margin: 0; line-height: 1.6;">{report['strength']}</p>
            </div>
            """, unsafe_allow_html=True)

        with sw_col2:
            st.markdown(f"""
            <div class="weakness-card fade-in">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.25rem;">📈</span>
                    <span style="font-weight: 600; color: #991B1B;">Areas to Improve</span>
                </div>
                <p style="color: #991B1B; margin: 0; line-height: 1.6;">{report['weakness']}</p>
            </div>
            """, unsafe_allow_html=True)

        # ── Charts ─────────────────────────────────────────────────────────────
        st.markdown('<div class="section-header" style="margin-top: 1.5rem;">Performance Visualization</div>', unsafe_allow_html=True)

        chart_col, radar_col = st.columns([3, 2])
        with chart_col:
            st.markdown("""
            <div class="enterprise-card scale-in">
                <div style="font-weight: 600; color: #111827; margin-bottom: 0.5rem;">Score Per Question</div>
                <div style="font-size: 0.75rem; color: #6B7280;">Individual question performance breakdown</div>
            """, unsafe_allow_html=True)
            st.image(_bar_chart(st.session_state.scores), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with radar_col:
            st.markdown("""
            <div class="enterprise-card scale-in">
                <div style="font-weight: 600; color: #111827; margin-bottom: 0.5rem;">Skill Radar</div>
                <div style="font-size: 0.75rem; color: #6B7280;">Multi-dimensional performance analysis</div>
            """, unsafe_allow_html=True)
            st.image(_radar_chart(report["technical_score"], report["communication_score"], report["confidence_score"]), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Integrity Report ──────────────────────────────────────────────────
        st.markdown('<div class="section-header" style="margin-top: 1.5rem;">Exam Integrity</div>', unsafe_allow_html=True)

        card_class = "enterprise-card-danger" if integrity["overall"] == "⚠️ Review Required" else "enterprise-card-success"
        st.markdown(f"""
        <div class='{card_class} fade-in'>
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 1.5rem;">{'🔒' if integrity['overall'] == '✅ Clean' else '⚠️'}</span>
                <div>
                    <div style="font-weight: 600; color: #111827;">Overall Integrity Status</div>
                    <div style="font-size: 1.1rem; font-weight: 600; margin: 0;">{integrity['overall']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        integrity_cols = st.columns(4)
        integrity_data = [
            {"label": "Tab Switches", "value": integrity['tab_switch_count'], "flagged": integrity['tab_flagged'], "icon": "🔄"},
            {"label": "Copy-Paste", "value": "Detected" if integrity['paste_detected'] else "None", "flagged": integrity['paste_detected'], "icon": "📋"},
            {"label": "Fullscreen Exits", "value": integrity['fullscreen_exit_count'], "flagged": integrity['fullscreen_flagged'], "icon": "🖥️"},
            {"label": "Auto Snapshots", "value": integrity['auto_snapshot_count'], "flagged": False, "icon": "📸"}
        ]

        for col, data in zip(integrity_cols, integrity_data):
            with col:
                color = "#EF4444" if data['flagged'] else "#10B981"
                st.markdown(f"""
                <div class="enterprise-card" style="border-top: 4px solid {color};">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                        <span>{data['icon']}</span>
                        <span style="font-size: 0.7rem; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.04em;">{data['label']}</span>
                    </div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: {color}; margin: 0.25rem 0;">{data['value']}</div>
                    <div style="font-size: 0.75rem; color: {color};">
                        {'⚠️ Flagged' if data['flagged'] else '✅ Clean'}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ── Question Breakdown ────────────────────────────────────────────────
        st.markdown('<div class="section-header" style="margin-top: 1.5rem;">Detailed Question Analysis</div>', unsafe_allow_html=True)

        for i, (q, a, s) in enumerate(zip(st.session_state.questions, st.session_state.answers, st.session_state.scores)):
            score_color = "#10B981" if s >= 70 else "#F59E0B" if s >= 50 else "#EF4444"
            with st.expander(f"Q{i+1}  ·  {q[:75]}{'...' if len(q)>75 else ''}  —  {s}/100"):
                st.markdown(f"""
                <div style="margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-weight: 600; color: #111827;">Question {i+1}</span>
                        <span style="background: {score_color}; color: white; padding: 0.125rem 0.75rem; border-radius: 99px; font-weight: 600; font-size: 0.75rem;">{s}/100</span>
                    </div>
                    <p style="color: #111827; font-size: 0.9rem; line-height: 1.6;">{q}</p>
                </div>
                <div style="background: #F8FAFC; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem;">
                    <div style="font-weight: 600; color: #111827; font-size: 0.8rem; margin-bottom: 0.25rem;">Your Answer:</div>
                    <p style="color: #6B7280; font-size: 0.875rem; line-height: 1.6; margin: 0;">{a if a else 'No answer provided'}</p>
                </div>
                """, unsafe_allow_html=True)

                ev_results = st.session_state.get("evaluation_results", [])
                if i < len(ev_results) and ev_results[i]:
                    ev = ev_results[i]
                    if ev.get("feedback"):
                        st.info(f"💡 {ev['feedback']}")
                    if ev.get("missing_points"):
                        st.warning(f"📌 {ev['missing_points']}")
                    if ev.get("ideal_answer"):
                        st.success(f"✨ {ev['ideal_answer']}")

        # ── Export ────────────────────────────────────────────────────────────
        st.markdown('<div class="section-header" style="margin-top: 1.5rem;">Export & Next Steps</div>', unsafe_allow_html=True)

        exp_col1, exp_col2, exp_col3 = st.columns([1, 1, 2])
        with exp_col1:
            if st.button("📄 Generate PDF", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    pdf_bytes = generate_pdf(
                        candidate_name=name_display, role=role, level=level,
                        interview_type=interview_type, scores=st.session_state.scores,
                        answers=st.session_state.answers, questions=st.session_state.questions,
                        evaluation_results=st.session_state.get("evaluation_results", []),
                        report=report
                    )
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"report_{name_display.replace(' ','_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        with exp_col2:
            if st.button("🔄 New Interview", use_container_width=True):
                reset_interview()
                st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# HISTORY TAB
# ═════════════════════════════════════════════════════════════════════════════
with history_tab:

    st.markdown(f"""
    <div class="section-header">Interview History</div>
    <div class="section-title">Your Past Interviews</div>
    <div class="section-subtitle">Review your previous practice sessions and track your progress over time</div>
    """, unsafe_allow_html=True)

    interviews = get_user_interviews(user["id"])

    if not interviews:
        st.markdown("""
        <div class="enterprise-card-premium" style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 0.75rem;">📋</div>
            <p style="color: #6B7280; margin: 0; font-size: 1rem; font-weight: 500;">No interviews yet</p>
            <p style="color: #9CA3AF; margin: 0.25rem 0 0; font-size: 0.875rem;">Complete your first interview to see your history here.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.caption(f"{len(interviews)} interview{'s' if len(interviews)>1 else ''} on record")

        for interview in interviews:
            band_emoji = "🟢" if interview["band"] == "Strong" else "🟡" if interview["band"] == "Average" else "🔴"
            with st.expander(f"{band_emoji}  {interview['display_date']}  ·  {interview['role']} ({interview['level']})  ·  Avg: {interview['average_score']}/100"):
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Average", f"{interview['average_score']}/100")
                with c2: st.metric("Technical", f"{interview['technical_score']}/100")
                with c3: st.metric("Communication", f"{interview['communication_score']}/100")
                with c4: st.metric("Confidence", f"{interview['confidence_score']}/100")
                st.markdown(f"<div style='color:#6B7280; font-size:0.85rem; margin:0.8rem 0;'>{interview['interview_type']} · {interview['question_source']} · {interview['evaluation_mode']} · {interview['total_questions']} questions</div>", unsafe_allow_html=True)
                if interview["scores"]:
                    score_cols = st.columns(len(interview["scores"]))
                    for i, (col, score) in enumerate(zip(score_cols, interview["scores"])):
                        with col: st.metric(f"Q{i+1}", f"{score}/100")
                dl_col, del_col, _ = st.columns([1, 1, 3])
                with dl_col:
                    if st.button("Generate PDF", key=f"pdf_{interview['id']}"):
                        hist_report = {
                            "total_questions": interview["total_questions"],
                            "average_score": interview["average_score"],
                            "technical_score": interview["technical_score"],
                            "communication_score": interview["communication_score"],
                            "confidence_score": interview["confidence_score"],
                            "band": interview["band"],
                            "strength": "Strong technical understanding." if interview["average_score"] >= 80 else "Good foundation." if interview["average_score"] >= 60 else "Willing to attempt questions.",
                            "weakness": "Minor improvements needed." if interview["average_score"] >= 80 else "Need more detailed answers." if interview["average_score"] >= 60 else "Need stronger technical knowledge."
                        }
                        with st.spinner("Generating..."):
                            pdf_bytes = generate_pdf(
                                candidate_name=interview["candidate_name"] or user["name"],
                                role=interview["role"], level=interview["level"],
                                interview_type=interview["interview_type"],
                                scores=interview["scores"], answers=interview["answers"],
                                questions=interview["questions"],
                                evaluation_results=interview["evaluation_results"],
                                report=hist_report
                            )
                        st.download_button(label="⬇️ Download PDF", data=pdf_bytes,
                            file_name=f"report_{interview['role'].replace(' ','_')}.pdf",
                            mime="application/pdf", key=f"dl_{interview['id']}")
                with del_col:
                    if st.button("🗑️ Delete", key=f"del_{interview['id']}"):
                        delete_interview(interview["id"], user["id"])
                        st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# DEV TOOLS TAB
# ═════════════════════════════════════════════════════════════════════════════

if DEV_MODE:

    with test_tab:
        st.markdown("""
        <div class="section-header">Developer Tools</div>
        <div class="section-title">Gemini AI Integration</div>
        <div class="section-subtitle">Test your Gemini API connection and evaluation capabilities</div>
        """, unsafe_allow_html=True)

        t1, t2 = st.columns(2)
        with t1:
            st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
            if st.button("🔌 Test Gemini Connection", use_container_width=True):
                try:
                    response = test_gemini()
                    st.success("✅ Connected successfully!")
                    st.markdown(f"<div style='background:#F8FAFC; padding:1rem; border-radius:8px; margin-top:0.5rem;'><code style='font-size:0.8rem;'>{response}</code></div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)

        with t2:
            st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
            if st.button("🧠 Test Gemini Evaluation", use_container_width=True):
                try:
                    result = evaluate_with_gemini("What is Python?", "Python is a programming language.")
                    st.success("✅ Evaluation complete!")
                    st.metric("Score", f"{result['score']}/100")
                    if result.get("feedback"): st.info(f"💡 {result['feedback']}")
                    if result.get("missing_points"): st.warning(f"📌 {result['missing_points']}")
                    if result.get("ideal_answer"): st.success(f"✨ {result['ideal_answer']}")
                except Exception as e:
                    st.error(f"❌ Evaluation failed: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)