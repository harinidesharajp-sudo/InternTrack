# 🎓 InternTrack: University Internship Management System
Project 35. Database Management System for Internship Application and Progress Monitoring 

> A 12-table 3NF Normalized Relational Database Management System (RDBMS) for university internship applications, faculty approvals, mentor assignments, daily work tracking, dual performance evaluations, and certification. This Repository consists of all the code files related to the application and also the PPT related to the project.

---

## 🌟 Architecture & Tech Stack

* **Backend**: Python Flask (`app.py`) with native MySQL connector (`db.py`) and embedded SQLite fallback for zero-dependency local runs[cite: 5].
* **Frontend**: Pitch-black OLED dark theme (`#030712`) built with Tailwind CSS and React/Vite[cite: 5].
* **Database Schema**: Full DDL compliance ensuring strict 3NF normalization across 12 relational entities[cite: 5].

---

## 🏛️ The 12 Normalized Relational Entities

1. **`Students`**: Student candidate academic records, departments, CGPA, and contact info[cite: 5].
2. **`Organizations`**: Host corporate entities, industries, addresses, and contacts[cite: 5].
3. **`Opportunities`**: Verified internship job posts put up by companies with stipends, locations, and openings[cite: 5].
4. **`Faculty_Mentors`**: Academic faculty members, departments, and designations[cite: 5].
5. **`Company_Supervisors`**: Corporate supervisors assigned by host organizations[cite: 5].
6. **`Applications`**: Student application submissions with Statements of Purpose and initial review states[cite: 5].
7. **`Approvals`**: Academic faculty evaluations verifying syllabus alignment and prerequisites[cite: 5].
8. **`Assignments`**: Tripartite internship binding of student, faculty mentor, and company supervisor with start and end dates[cite: 5].
9. **`Weekly_Logs`**: Daily work schedule and tasks to perform assigned to the student, paired with submitted work reports, hours worked, and mentor review feedback[cite: 5].
10. **`Evaluations`**: Dual independent performance scorecards submitted by both the Faculty Mentor and Company Supervisor (technical scores, professionalism scores, and written remarks)[cite: 5].
11. **`Certificates`**: Completion credentials with grade classification and verification checksum[cite: 5].
12. **`Feedback`**: 360-degree qualitative reviews and 1–5 star ratings from students, mentors, and corporate supervisors[cite: 5].


## 🚀 Getting Started Locally (VS Code)

### Frontend (React & Vite) and Backend (Python Flask & Database)
To run the interactive React frontend development server and backend database:
```bash
# Install dependencies (use legacy peer deps if needed)
npm install --legacy-peer-deps

# Start the Vite development server
npm run dev
---

## 🚀 Getting Started Locally in VS Code

### Run the Backend (Python Flask & Database)
Open your integrated terminal in Visual Studio Code (`Ctrl + ~`) and follow these commands:

```bash
# 1. Create a Python virtual environment
python -m venv venv

# 2. Activate the virtual environment
# On Windows (Command Prompt / PowerShell):
venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Start the Flask backend server
python app.py
