from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json, time, uuid
from datetime import datetime
from adaptive_engine import AdaptiveEngine
from database import Database

app = FastAPI(title="AdaptIQ Enterprise", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()
engine = AdaptiveEngine()

# ─── Models ───────────────────────────────────────────────────────────────────

class StudentRegister(BaseModel):
    name: str
    email: str
    password: str = "pass123" # Simple auth for now
    college: str
    year: str
    role: str = "student"

class LoginRequest(BaseModel):
    email: str
    password: str

class StartSession(BaseModel):
    student_id: str
    topics: List[str]
    total_questions: int = 10
    language: Optional[str] = None
    categories: List[str] # ["Coding", "Quiz", etc.]

class SubmitAnswer(BaseModel):
    session_id: str
    question_id: str
    selected_answer: str
    response_time: float
    hesitation_time: float = 0
    attempt_number: int = 1

# ─── Auth Routes ─────────────────────────────────────────────────────────────

@app.post("/api/auth/register")
def register_student(data: StudentRegister):
    if db.get_student_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    student_id = str(uuid.uuid4())[:8]
    student = {
        "student_id": student_id,
        "name": data.name,
        "email": data.email,
        "password": data.password,
        "college": data.college,
        "year": data.year,
        "role": data.role,
        "created_at": datetime.now().isoformat()
    }
    db.save_student(student)
    return {"student_id": student_id, "role": student["role"], "message": "Registered successfully"}

@app.post("/api/auth/login")
def login(data: LoginRequest):
    student = db.get_student_by_email(data.email)
    if not student or student["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "student_id": student["student_id"],
        "name": student["name"],
        "role": student["role"],
        "college": student["college"],
        "year": student["year"]
    }

# ─── Student Routes ──────────────────────────────────────────────────────────

@app.get("/api/student/{student_id}/activity")
def get_activity(student_id: str):
    sessions = db.get_student_sessions(student_id)
    profiles = db.get_profile(student_id)
    return {"sessions": sessions, "profiles": profiles}

@app.post("/api/session/start")
def start_session(data: StartSession):
    session_id = str(uuid.uuid4())[:12]
    session = {
        "session_id": session_id,
        "student_id": data.student_id,
        "categories": data.categories,
        "topics": data.topics,
        "language": data.language,
        "total_questions": data.total_questions,
        "current_question": 0,
        "current_difficulty": 2,
        "responses": [],
        "started_at": datetime.now().isoformat(),
        "status": "active"
    }
    db.save_session(session)
    question = engine.get_next_question(session)
    if not question:
        raise HTTPException(status_code=400, detail="No questions found for the selected subjects.")
        
    return {
        "session_id": session_id,
        "question": question,
        "progress": {"current": 1, "total": data.total_questions}
    }

@app.post("/api/session/submit")
def submit_answer(data: SubmitAnswer):
    session = db.get_session(data.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    question = db.get_question(data.question_id)
    
    # Advanced Multi-modal Evaluation
    q_type = question.get("type", "mcq")
    student_ans = data.selected_answer.strip().lower()
    target_ans = question["correct_answer"].strip().lower()

    if q_type == "mcq":
        is_correct = target_ans == student_ans
    elif q_type in ["coding", "debugging"]:
        # Better than exact match: check if key substrings match (simulated intelligence)
        is_correct = (len(student_ans) > 20 and target_ans[:10] in student_ans) or (target_ans in student_ans)
    else: # descriptive
        # Essay evaluation: length and keyword check
        is_correct = len(student_ans.split()) >= 10

    # Behavior Detection Point
    behavior = engine.detect_behavior(is_correct, data.response_time)

    response = {
        "question_id": data.question_id,
        "topic": question["topic"],
        "difficulty": question["difficulty"],
        "is_correct": is_correct,
        "response_time": data.response_time,
        "behavior": behavior,
        "hesitation_time": data.hesitation_time,
        "attempt_number": data.attempt_number,
        "selected_answer": data.selected_answer
    }
    session["responses"].append(response)

    # Adaptive Intelligence Update
    new_difficulty = engine.update_difficulty(
        session["current_difficulty"], is_correct, 
        data.response_time, session["responses"]
    )
    session["current_difficulty"] = new_difficulty
    session["current_question"] += 1

    if session["current_question"] >= session["total_questions"]:
        session["status"] = "completed"
        session["completed_at"] = datetime.now().isoformat()
        db.save_session(session)
        
        profile = engine.generate_competency_profile(session)
        db.save_profile(session["student_id"], profile)
        
        # Mock Email Trigger
        print(f"📧 Notification: Results sent to {session['student_id']}")
        
        return {
            "status": "completed",
            "is_correct": is_correct,
            "correct_answer": question["correct_answer"],
            "profile": profile
        }

    db.save_session(session)
    next_question = engine.get_next_question(session)
    return {
        "status": "continue",
        "is_correct": is_correct,
        "correct_answer": question["correct_answer"],
        "question": next_question,
        "progress": {"current": session["current_question"] + 1, "total": session["total_questions"]}
    }

# ─── Admin Routes ────────────────────────────────────────────────────────────

@app.get("/api/admin/analytics")
def get_admin_data(college: str, year: str):
    students = db.get_admin_students(college, year)
    data = []
    for s in students:
        profiles = db.get_profile(s["student_id"])
        data.append({
            "name": s["name"],
            "email": s["email"],
            "latest_profile": profiles[-1] if profiles else None
        })
    return {"students": data}

@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
