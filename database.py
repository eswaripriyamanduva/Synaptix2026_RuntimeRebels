"""
Database Layer
Uses JSON files for simplicity — easy to swap with PostgreSQL or MongoDB.
See comments marked with # POSTGRES and # MONGO for migration hints.
"""

import json
import os
from typing import List, Optional, Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def _load(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def _save(filename: str, data: dict):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


class Database:

    # ── Students & Auth ──────────────────────────────────────────────────────────────
    def save_student(self, student: dict):
        # Save Profile
        students = _load("students.json")
        sid = student["student_id"]
        students[sid] = {
            "student_id": sid,
            "name": student["name"],
            "email": student["email"],
            "college": student.get("college", "VITS"),
            "year": student.get("year", "1"),
            "created_at": student.get("created_at")
        }
        _save("students.json", students)
        
        # Save Credentials
        auth = _load("auth.json")
        auth[student["email"]] = {
            "student_id": sid,
            "email": student["email"],
            "password": student["password"],
            "role": student.get("role", "student")
        }
        _save("auth.json", auth)

    def get_student(self, student_id: str) -> Optional[dict]:
        # Merge profile and credentials for backward compatibility in current routes
        profile = _load("students.json").get(student_id)
        if not profile: return None
        
        auth_db = _load("auth.json")
        for auth in auth_db.values():
            if auth["student_id"] == student_id:
                return {**profile, **auth}
        return profile

    def get_student_by_email(self, email: str) -> Optional[dict]:
        auth = _load("auth.json").get(email)
        if not auth: return None
        
        profile = _load("students.json").get(auth["student_id"])
        if not profile: return auth # Return what we have
        return {**profile, **auth}

    def get_admin_students(self, college: str, year: str) -> List[dict]:
        colleges = _load("colleges.json")
        students = _load("students.json")
        student_ids = colleges.get(college, {}).get(year, [])
        return [students[sid] for sid in student_ids if sid in students]

    # ─── Questions ───────────────────────────────────────────────────────────
    def get_questions_by_filter(
        self,
        topics: List[str],
        difficulty: int,
        exclude_ids: List[str],
        language: Optional[str] = None,
        categories: Optional[List[str]] = None
    ) -> List[dict]:
        db = _load("questions.json")
        filtered = []
        
        # Normalize inputs
        topics_lower = [t.lower() for t in topics]
        cat_lower = [c.lower() for c in categories] if categories else []

        for q in db.values():
            if q["question_id"] in exclude_ids:
                continue
            if q["difficulty"] != difficulty:
                continue
            
            # Topic check (Case-insensitive)
            q_topic = q.get("topic", "").lower()
            if q_topic not in topics_lower:
                continue
                
            # Category check (Case-insensitive)
            if cat_lower:
                q_cat = q.get("category", "").lower()
                if q_cat not in cat_lower:
                    continue
            
            # Language check
            if language and q.get("language") != language:
                continue
                
            filtered.append(q)
            
        return filtered

    def get_question(self, question_id: str) -> Optional[dict]:
        db = _load("questions.json")
        return db.get(question_id)

    def get_all_topics(self) -> List[str]:
        db = _load("questions.json")
        return list(set(q["topic"] for q in db.values()))

    # ─── Sessions & Profiles ──────────────────────────────────────────────────
    def save_session(self, session: dict):
        sessions = _load("sessions.json")
        sessions[session["session_id"]] = session
        _save("sessions.json", sessions)

    def get_session(self, session_id: str) -> Optional[dict]:
        sessions = _load("sessions.json")
        return sessions.get(session_id)

    def save_profile(self, student_id: str, profile: dict):
        profiles = _load("profiles.json")
        if student_id not in profiles: profiles[student_id] = []
        profiles[student_id].append(profile)
        _save("profiles.json", profiles)

    def get_profile(self, student_id: str) -> List[dict]:
        profiles = _load("profiles.json")
        return profiles.get(student_id, [])

    def get_student_sessions(self, student_id: str) -> List[dict]:
        sessions = _load("sessions.json")
        return [s for s in sessions.values() if s["student_id"] == student_id]
