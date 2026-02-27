import json
import os

data_dir = os.path.join(os.path.dirname(__file__), "data")
students_path = os.path.join(data_dir, "students.json")
auth_path = os.path.join(data_dir, "auth.json")

if os.path.exists(students_path):
    with open(students_path, "r") as f:
        students = json.load(f)
    
    auth = {}
    new_students = {}
    
    for sid, s in students.items():
        email = s.get("email")
        if not email: continue
        
        # Split data
        auth[email] = {
            "student_id": sid,
            "email": email,
            "password": s.get("password", "pass123"),
            "role": s.get("role", "student")
        }
        
        new_students[sid] = {
            "student_id": sid,
            "name": s.get("name", "Unknown"),
            "email": email,
            "college": s.get("college", "VITS"),
            "year": s.get("year", "1"),
            "created_at": s.get("created_at")
        }
        
    with open(auth_path, "w") as f:
        json.dump(auth, f, indent=2)
    
    with open(students_path, "w") as f:
        json.dump(new_students, f, indent=2)
        
    print(f"Migration successful. Created auth.json with {len(auth)} records and updated students.json.")
else:
    print("students.json not found, nothing to migrate.")
