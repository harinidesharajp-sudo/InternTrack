# InternTrack: University Internship Management System

A 12-table 3NF Normalized Relational Database Management System (RDBMS) for University Internship Applications, Faculty Approvals, Mentor Assignments, Daily Work Tracking, Dual Evaluations, and Certification.

## 12 Normalized Relational Entities (Strict 3NF Compliance)

1. **`Students`**: Student candidate academic records, departments, CGPA, and contact info.
2. **`Organizations`**: Host corporate entities, industries, addresses, and contacts.
3. **`Opportunities`**: Verified internship job posts put up by companies with stipends, locations, and openings.
4. **`Faculty_Mentors`**: Academic faculty members, departments, and designations.
5. **`Company_Supervisors`**: Corporate supervisors assigned by host organizations.
6. **`Applications`**: Student application submissions with Statements of Purpose and initial review states.
7. **`Approvals`**: Academic faculty evaluations verifying syllabus alignment and prerequisites.
8. **`Assignments`**: Tripartite internship binding of student, faculty mentor, and company supervisor with start and end dates.
9. **`Weekly_Logs`**: Daily work schedule and tasks to perform assigned to the student, paired with submitted work reports, hours worked, and mentor review feedback.
10. **`Evaluations`**: Dual independent performance scorecards submitted by both the Faculty Mentor and Company Supervisor (technical scores, professionalism scores, and comprehensive written remarks).
11. **`Certificates`**: Completion credentials with grade classification and verification checksum.
12. **`Feedback`**: 360-degree qualitative reviews and 1-5 star ratings from students, mentors, and corporate supervisors.

## Architecture

- **Backend**: Python Flask (`app.py`) with native MySQL connector (`db.py`) and embedded SQLite fallback for zero-dependency local runs.
- **Database Schema**: Full DDL script in `schema.sql` with foreign key cascades, unique indexes, and domain checks.
- **Frontend**: Pitch-black OLED dark theme (`#030712`) built with Tailwind CSS and React/Vite.
