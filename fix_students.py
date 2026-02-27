import json
import os

path = os.path.join("data", "students.json")
if os.path.exists(path):
    with open(path, "r") as f:
        data = json.load(f)
    
    updated = False
    for sid, student in data.items():
        if "password" not in student:
            student["password"] = "pass123"
            updated = True
        if "role" not in student:
            student["role"] = "student"
            updated = True
        if "college" not in student:
            student["college"] = "Unknown"
            updated = True
        if "year" not in student:
            student["year"] = "1"
            updated = True
            
    if updated:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print("Successfully updated students.json with default credentials (password: pass123)")
    else:
        print("No updates needed for students.json")
else:
    print("students.json not found")
