# 🎯 AI Interview Coach

> A full-stack AI-powered interview preparation platform built with Python and Streamlit.  
> Practice technical and HR interviews, get real-time AI feedback, analyse your body language, and download a professional PDF report.

---

## 🚀 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## 📸 Screenshots

> *(Add screenshots of the app here after deployment)*

---

## ✨ Features

### 🎤 Interview Engine
- Choose from **4 job roles** — Python Developer, Java Developer, Data Analyst, Frontend Developer
- Select **experience level** — Beginner, Intermediate, Advanced
- Choose **interview type** — Technical, HR, Mixed
- **Static question bank** with curated questions per role and level
- **AI-generated questions** powered by Google Gemini — unique questions every session

### 🤖 AI Evaluation
- **Local evaluator** for instant offline feedback
- **Gemini AI evaluator** returns structured feedback:
  - Score out of 100
  - What was correct
  - Missing points
  - Ideal answer
- Evaluation screen after every question before moving forward

### 🎙️ Voice Input
- Browser-based voice recording using the **Web Speech API**
- Completely free — no API key required
- Works in Chrome and Edge
- Transcript fills the answer box for review before submission

### 📷 Webcam Analysis
- Opt-in webcam analysis using **OpenCV**
- Analyses each snapshot for:
  - Face detection
  - Eye contact / gaze direction
  - Posture score (centering, proximity, upper body visibility)
  - Confidence score (combined metric)
- Per-question results shown on evaluation screen
- Summary shown on final report

### 📊 Professional Report
- Generated at interview completion with:
  - Overall average score
  - Technical, Communication, and Confidence scores
  - Performance band — Strong / Average / Weak
  - Strength and weakness summary
  - Score per question bar chart
  - Performance radar chart
  - Per-question breakdown with AI feedback and ideal answers
- **PDF export** — download a professional report with all charts and answers

### 🔐 Authentication
- Register and login with email and password
- Passwords hashed with **bcrypt**
- Session management via Streamlit session state

### 📋 Interview History
- Every completed interview saved automatically to **SQLite**
- View all past interviews with full score breakdown
- Re-download PDF for any historical interview
- Delete interviews you no longer need

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI / LLM | Google Gemini 2.5 Flash |
| Voice Input | Web Speech API (browser-native) |
| Computer Vision | OpenCV (Haar Cascades) |
| Charts | Matplotlib |
| PDF Generation | fpdf2 |
| Database | SQLite |
| Auth | bcrypt |
| Language | Python 3.12 |

---

## 📁 Project Structure

```
ai-interview-coach/
│
├── app.py                          # Main Streamlit application
│
├── modules/
│   ├── ai_evaluator.py             # Local length-based evaluator
│   ├── auth_service.py             # Register, login, password hashing
│   ├── db_service.py               # SQLite setup and interview history
│   ├── gemini_service.py           # Gemini API — evaluation + question generation
│   ├── interview_engine.py         # Static question bank
│   ├── report_generator.py         # Charts, report data, PDF export
│   ├── session_manager.py          # Streamlit session state management
│   ├── voice_service.py            # Web Speech API HTML component
│   └── webcam_service.py           # OpenCV webcam snapshot analysis
│
├── requirements.txt                # Python dependencies
├── .env                            # API keys (not committed to Git)
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-interview-coach.git
cd ai-interview-coach
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your free Gemini API key at [https://aistudio.google.com](https://aistudio.google.com)

### 5. Run the application

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔑 Environment Variables

| Variable | Description | Required |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |

---

## 📦 Dependencies

```
streamlit
google-generativeai
python-dotenv
opencv-python
Pillow
matplotlib
fpdf2
bcrypt
numpy
mediapipe
```

---

## 🗺️ Development Roadmap

| Phase | Feature | Status |
|---|---|---|
| 1 | Clean interview flow with evaluation screen | ✅ Complete |
| 2 | Gemini structured scoring (score + feedback + ideal answer) | ✅ Complete |
| 3 | AI-generated questions via Gemini | ✅ Complete |
| 4 | Voice interview with Web Speech API | ✅ Complete |
| 5 | Webcam analysis with OpenCV | ✅ Complete |
| 6 | Professional report with charts and PDF export | ✅ Complete |
| 7 | User authentication and interview history | ✅ Complete |
| 8 | Cloud deployment | 🚧 In Progress |

---

## 🧠 How It Works

```
User logs in / registers
        ↓
Selects role, level, type, evaluation mode, question source
        ↓
Interview begins — questions served one at a time
        ↓
User answers via text or voice
        ↓
Answer evaluated (Local or Gemini AI)
        ↓
Evaluation screen — score, feedback, missing points, ideal answer
        ↓
Optional webcam snapshot analysed for posture and eye contact
        ↓
Next question → repeat
        ↓
Interview complete → Report generated
        ↓
Charts rendered (bar + radar)
        ↓
Interview saved to SQLite history
        ↓
PDF report available for download
```

---

## 🔒 Security Notes

- Passwords are hashed using **bcrypt** before storage — plain text passwords are never saved
- API keys are stored in `.env` and excluded from version control via `.gitignore`
- The SQLite database file is local to the deployment environment

---

## 👤 Author

**Tirth Modi**  
DevOps Engineer | AI Enthusiast  
[GitHub](https://github.com/YOUR_USERNAME) · [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)

---

> Built with ❤️ using Python, Streamlit, and AI