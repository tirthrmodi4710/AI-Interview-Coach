import cv2
import numpy as np
from PIL import Image
import io
import base64

print("========== OpenCV Debug ==========")
print("cv2 module:", cv2)
print("cv2 file:", getattr(cv2, "__file__", "No __file__"))
print("cv2 version:", getattr(cv2, "__version__", "No version"))
print("Has CascadeClassifier:", hasattr(cv2, "CascadeClassifier"))
print("cv2.data:", getattr(cv2, "data", "No data"))
print("==================================")

# Load cascade classifiers once at module level
_face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
_eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)

def analyze_pil_image(pil_image):
    """
    Accepts a PIL Image (from st.camera_input).
    Returns a dict with face_detected, looking_at_screen,
    posture_score, confidence_score, and feedback list.
    """

    result = {
        "face_detected": False,
        "looking_at_screen": False,
        "posture_score": 0,
        "confidence_score": 0,
        "feedback": []
    }

    try:
        frame = np.array(pil_image.convert("RGB"))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = frame.shape[:2]

        # ── Face Detection ───────────────────────────────────────────────────
        faces = _face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        if len(faces) == 0:
            result["feedback"].append(
                "No face detected. Make sure your face is visible and well-lit."
            )
            return result

        result["face_detected"] = True

        # Use the largest detected face
        face = max(faces, key=lambda f: f[2] * f[3])
        fx, fy, fw, fh = face

        # ── Posture Score ────────────────────────────────────────────────────
        posture_score = 100

        # Check 1: Face centered horizontally (±25% from center)
        face_center_x = fx + fw / 2
        horizontal_offset = abs(face_center_x - w / 2) / (w / 2)
        if horizontal_offset > 0.25:
            posture_score -= 25
            result["feedback"].append("Center yourself in the frame horizontally.")

        # Check 2: Face not too low in frame
        face_center_y = fy + fh / 2
        if face_center_y > h * 0.65:
            posture_score -= 25
            result["feedback"].append("Sit up — your face is too low in the frame.")

        # Check 3: Close enough to camera
        face_area_ratio = (fw * fh) / (w * h)
        if face_area_ratio < 0.04:
            posture_score -= 25
            result["feedback"].append("Sit closer to the camera.")
        elif face_area_ratio > 0.5:
            posture_score -= 15
            result["feedback"].append("Sit slightly further from the camera.")

        result["posture_score"] = max(0, posture_score)

        # ── Eye Contact Detection ────────────────────────────────────────────
        face_roi_gray = gray[fy:fy + fh, fx:fx + fw]
        eyes = _eye_cascade.detectMultiScale(
            face_roi_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(20, 20)
        )

        if len(eyes) >= 2:
            result["looking_at_screen"] = True
        else:
            result["looking_at_screen"] = False
            result["feedback"].append("Maintain eye contact with the camera.")

        # ── Confidence Score ─────────────────────────────────────────────────
        gaze_score = 100 if result["looking_at_screen"] else 50
        face_score = 100

        result["confidence_score"] = int(
            (face_score * 0.3) +
            (gaze_score * 0.4) +
            (result["posture_score"] * 0.3)
        )

        if not result["feedback"]:
            result["feedback"].append("Great posture and eye contact! Keep it up.")

    except Exception as e:
        result["feedback"].append(f"Analysis error: {str(e)}")

    return result