# 🎓 InternTrack: University Internship Management System

> A 12-table 3NF Normalized Relational Database Management System (RDBMS) designed for university internship applications, faculty approvals, tripartite mentor assignments, daily work tracking, dual performance evaluations, and cryptographically verifiable certification.

---

## 🌟 Key Features & Architecture

* **Dual-Mode Execution**: Built with a robust Python/Flask backend (`app.py`) featuring native MySQL support and an embedded SQLite fallback, alongside a blazing-fast React/Vite single-page frontend.
* **OLED Dark-Mode UI**: Crafted with a pitch-black OLED color palette (`#030712`) and Tailwind CSS for a sleek, modern, professional developer experience.
* **Strict 3NF Normalization**: Features exactly 12 fully normalized relational database entities ensuring data integrity, cascading foreign keys, and zero redundancy.

---

## 🏛️ The 12 Normalized Relational Entities

1. **`Students`**: Student candidate academic records, departments, CGPA, and contact information[cite: 5].
2. **`Organizations`**: Host corporate entities, industry sectors, addresses, and contact details[cite: 5].
3. **`Opportunities`**: Verified internship job posts created by partner companies featuring stipends, locations, and opening quotas[cite: 5].
4. **`Faculty_Mentors`**: Academic faculty members, departments, and professional designations[cite: 5].
5. **`Company_Supervisors`**: Corporate supervisors assigned by host organizations[cite: 5].
6. **`Applications`**: Student application submissions complete with Statements of Purpose and tracking states[cite: 5].
7. **`Approvals`**: Academic faculty evaluations verifying syllabus alignment and prerequisite coursework[cite: 5].
8. **`Assignments`**: Tripartite internship binding of Student $\times$ Faculty Mentor $\times$ Company Supervisor with active timelines[cite: 5].
9. **`Weekly_Logs`**: Daily work schedule and tasks assigned to perform, paired with student progress reports, hours worked, and mentor feedback[cite: 5].
10. **`Evaluations`**: Dual independent performance scorecards submitted by both the Faculty Mentor and Company Supervisor (technical & professionalism scores)[cite: 5].
11. **`Certificates`**: Completion credentials featuring grade classifications and tamper-evident verification codes[cite: 5].
12. **`Feedback`**: 360-degree qualitative reviews and 1–5 star ratings from students, faculty, and corporate supervisors[cite: 5].

---

## 🚀 Getting Started Locally (VS Code)

### 1. Frontend (React & Vite)
To run the interactive React frontend development server:
```bash
# Install dependencies (use legacy peer deps if needed)
npm install --legacy-peer-deps

# Start the Vite development server
npm run dev

### 2. Backend (Python)
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # On macOS/Linux: source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the Flask application
python app.py
