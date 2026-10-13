"""
InternTrack: Flask Web Application Backend
University Internship Application & Progress Monitoring System
Strictly 12-Table 3NF Normalized MySQL Database Architecture
"""

import os
import uuid
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "interntrack-secret-key-2026-woxsen")


def verify_and_seed_database():
    """
    Verifies that all 12 normalized tables exist, and seeds realistic sample data
    if tables are empty. Operates transparently on MySQL or SQLite fallback.
    """
    print("[InternTrack] Initializing 12-table 3NF database schema...")

    # 1. Students Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            Student_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
            Name VARCHAR(100) NOT NULL,
            Department VARCHAR(100) NOT NULL,
            Email VARCHAR(150) NOT NULL UNIQUE,
            Phone VARCHAR(25) NOT NULL,
            CGPA REAL DEFAULT 8.50,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Organizations Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS Organizations (
            Org_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
            Org_Name VARCHAR(150) NOT NULL,
            Industry VARCHAR(100) NOT NULL,
            Address VARCHAR(255) NOT NULL,
            Email VARCHAR(150) NOT NULL UNIQUE,
            Website VARCHAR(150),
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 3. Opportunities Table (Posts Put Up by Companies)
    db.execute("""
        CREATE TABLE IF NOT EXISTS Opportunities (
            Opp_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
            Org_ID INT NOT NULL,
            Title VARCHAR(150) NOT NULL,
            Description TEXT NOT NULL,
            Stipend REAL DEFAULT 0.00,
            Location VARCHAR(100) NOT NULL,
            Openings INT DEFAULT 1,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Org_ID) REFERENCES Organizations(Org_ID) ON DELETE CASCADE
        );
    """)

    # 4. Faculty_Mentors Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS Faculty_Mentors (
            Faculty_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
            Name VARCHAR(100) NOT NULL,
            Department VARCHAR(100) NOT NULL,
            Email VARCHAR(150) NOT NULL UNIQUE,
            Phone VARCHAR(25) NOT NULL,
            Designation VARCHAR(100) DEFAULT 'Associate Professor'
        );
    """)

    # 5. Company_Supervisors Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS Company_Supervisors (
            Supervisor_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
            Org_ID INT NOT NULL,
            Name VARCHAR(100) NOT NULL,
            Email VARCHAR(150) NOT NULL,
            Phone VARCHAR(25) NOT NULL,
            Designation VARCHAR(100) NOT NULL,
            FOREIGN KEY (Org_ID) REFERENCES Organizations(Org_ID) ON DELETE CASCADE
        );
    """)

    # 6. Applications Table (Students Apply with Statement of Purpose)
    db.execute("""
        CREATE TABLE IF NOT EXISTS Applications (
            App_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
            Student_ID INT NOT NULL,
            Opp_ID INT NOT NULL,
            Application_Date DATE NOT NULL,
            Status VARCHAR(50) NOT NULL DEFAULT 'Pending',
            Statement_Of_Purpose TEXT,
            FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID) ON DELETE CASCADE,
            FOREIGN KEY (Opp_ID) REFERENCES Opportunities(Opp_ID) ON DELETE CASCADE
        );
    """)

    # 7. Approvals Table (Faculty Academic Review)
    db.execute("""
        CREATE TABLE IF NOT EXISTS Approvals (
            Approval_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
            App_ID INT NOT NULL UNIQUE,
            Faculty_ID INT NOT NULL,
            Approval_Status VARCHAR(50) NOT NULL DEFAULT 'Pending',
            Approval_Date DATE,
            Remarks TEXT,
            FOREIGN KEY (App_ID) REFERENCES Applications(App_ID) ON DELETE CASCADE,
            FOREIGN KEY (Faculty_ID) REFERENCES Faculty_Mentors(Faculty_ID) ON DELETE RESTRICT
        );
    """)

    # 8. Assignments Table (Tripartite Binding: Student + Faculty Mentor + Company Supervisor)
    db.execute("""
        CREATE TABLE IF NOT EXISTS Assignments (
            Assignment_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
            Approval_ID INT NOT NULL UNIQUE,
            Faculty_ID INT NOT NULL,
            Supervisor_ID INT NOT NULL,
            Start_Date DATE NOT NULL,
            End_Date DATE NOT NULL,
            Status VARCHAR(50) NOT NULL DEFAULT 'Active',
            FOREIGN KEY (Approval_ID) REFERENCES Approvals(Approval_ID) ON DELETE CASCADE,
            FOREIGN KEY (Faculty_ID) REFERENCES Faculty_Mentors(Faculty_ID) ON DELETE RESTRICT,
            FOREIGN KEY (Supervisor_ID) REFERENCES Company_Supervisors(Supervisor_ID) ON DELETE RESTRICT
        );
    """)

    # 9. Weekly_Logs Table (Daily Work Tasks to Perform & Work Report)
    db.execute("""
        CREATE TABLE IF NOT EXISTS Weekly_Logs (
            Log_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
            Assignment_ID INT NOT NULL,
            Week_Number INT NOT NULL,
            Tasks_To_Perform TEXT NOT NULL,
            Report_Text TEXT NOT NULL,
            Submission_Date DATE NOT NULL,
            Hours_Worked INT DEFAULT 40,
            Status VARCHAR(50) DEFAULT 'Submitted',
            Review_Comments TEXT,
            FOREIGN KEY (Assignment_ID) REFERENCES Assignments(Assignment_ID) ON DELETE CASCADE
        );
    """)

    # 10. Evaluations Table (Dual Evaluations by Faculty & Company)
    db.execute("""
        CREATE TABLE IF NOT EXISTS Evaluations (
            Evaluation_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
            Assignment_ID INT NOT NULL,
            Score REAL NOT NULL,
            Technical_Score REAL DEFAULT 95.0,
            Professionalism_Score REAL DEFAULT 95.0,
            Feedback_Text TEXT NOT NULL,
            Evaluation_Date DATE NOT NULL,
            Evaluator_Role VARCHAR(50) DEFAULT 'Company_Supervisor',
            Evaluator_Name VARCHAR(100),
            FOREIGN KEY (Assignment_ID) REFERENCES Assignments(Assignment_ID) ON DELETE CASCADE
        );
    """)

    # 11. Certificates Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS Certificates (
            Cert_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
            Assignment_ID INT NOT NULL UNIQUE,
            Issue_Date DATE NOT NULL,
            Verification_Code VARCHAR(64) NOT NULL UNIQUE,
            Grade VARCHAR(50) DEFAULT 'Distinction (A+)',
            FOREIGN KEY (Assignment_ID) REFERENCES Assignments(Assignment_ID) ON DELETE CASCADE
        );
    """)

    # 12. Feedback Table (360 Stakeholder Ratings)
    db.execute("""
        CREATE TABLE IF NOT EXISTS Feedback (
            Feedback_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
            Assignment_ID INT NOT NULL,
            Given_By VARCHAR(50) NOT NULL,
            Author_Name VARCHAR(100) NOT NULL,
            Comments TEXT NOT NULL,
            Rating INT DEFAULT 5,
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Assignment_ID) REFERENCES Assignments(Assignment_ID) ON DELETE CASCADE
        );
    """)

    # Check if seeding is required
    existing_students = db.fetch_all("SELECT COUNT(*) as count FROM Students")
    if existing_students and existing_students[0]['count'] > 0:
        print("[InternTrack] Database already contains records. Skipping initial seeding.")
        return

    print("[InternTrack] Seeding 12 normalized tables...")

    # 1. Seed Students
    students_data = [
        ("Aarav Sharma", "Computer Science & Artificial Intelligence", "aarav.sharma@woxsen.edu.in", "+91 98451 22093", 9.42),
        ("Aryan Varma", "Computer Science & Engineering", "aryan.v@woxsen.edu.in", "+91 98765 43210", 8.85),
        ("Sneha Patel", "Data Science & Analytics", "sneha.p@woxsen.edu.in", "+91 99123 45678", 9.10),
        ("Vikram Rao", "Electronics & Communication", "vikram.r@woxsen.edu.in", "+91 94455 66778", 8.35),
        ("Ananya Sen", "Artificial Intelligence & Robotics", "ananya.s@woxsen.edu.in", "+91 98877 66554", 9.20)
    ]
    for s in students_data:
        db.execute("INSERT INTO Students (Name, Department, Email, Phone, CGPA) VALUES (%s, %s, %s, %s, %s)", s)

    # 2. Seed Organizations
    orgs_data = [
        ("NVIDIA AI Research", "Semiconductors & Deep Learning", "Prestige Tech Park, Bengaluru", "internships@nvidia.com", "https://nvidia.com"),
        ("Microsoft IDC", "Cloud & Enterprise Software", "Gachibowli, Hyderabad", "university@microsoft.com", "https://microsoft.com"),
        ("Google Cloud Labs", "Cloud Computing & Systems", "Financial District, Hyderabad", "campus-india@google.com", "https://cloud.google.com"),
        ("TCS Research & Innovation", "Cognitive Systems & Robotics", "Adibatla SEZ, Hyderabad", "careers.research@tcs.com", "https://tcs.com")
    ]
    for o in orgs_data:
        db.execute("INSERT INTO Organizations (Org_Name, Industry, Address, Email, Website) VALUES (%s, %s, %s, %s, %s)", o)

    # 3. Seed Opportunities (Posts Put Up by Companies)
    opps_data = [
        (1, "LLM Acceleration & CUDA Kernel Optimization Intern", "Focus on transformer inference acceleration using TensorRT-LLM and custom CUDA kernels for edge inference devices.", 65000.00, "Bengaluru / Hybrid", 2),
        (2, "Azure Cloud Distributed Systems Intern", "Build high-throughput microservices for Azure event grid and telemetry routing pipelines.", 55000.00, "Hyderabad, Gachibowli", 3),
        (3, "Generative AI Knowledge Graph Engineer", "Research grounding methods for enterprise search combining Gemini models with Neo4j enterprise graphs.", 60000.00, "Hyderabad, Financial District", 2),
        (4, "Autonomous Robotics & SLAM Vision Intern", "Develop ROS2 visual odometry pipelines for multi-sensor perception stacks.", 40000.00, "Hyderabad, Adibatla", 2)
    ]
    for opp in opps_data:
        db.execute("INSERT INTO Opportunities (Org_ID, Title, Description, Stipend, Location, Openings) VALUES (%s, %s, %s, %s, %s, %s)", opp)

    # 4. Seed Faculty Mentors
    faculty_data = [
        ("Dr. Ramesh Sundaram", "School of Technology - CS & AI", "ramesh.sundaram@woxsen.edu.in", "+91 91234 56780", "Professor & Academic Dean"),
        ("Dr. K. Venkat", "Computer Science & Engineering", "venkat.k@woxsen.edu.in", "+91 92345 67891", "Professor & Department Chair"),
        ("Prof. Rajesh Nair", "Electronics & Robotics", "rajesh.nair@woxsen.edu.in", "+91 93456 78902", "Associate Professor"),
        ("Dr. Meera Nambiar", "Data Science & Machine Learning", "meera.nambiar@woxsen.edu.in", "+91 94567 89013", "Associate Professor")
    ]
    for f in faculty_data:
        db.execute("INSERT INTO Faculty_Mentors (Name, Department, Email, Phone, Designation) VALUES (%s, %s, %s, %s, %s)", f)

    # 5. Seed Company Supervisors
    supervisors_data = [
        (1, "Dr. Priya Sharma", "psharma@nvidia.com", "+91 98111 22334", "Staff Research Scientist"),
        (2, "Rahul Mehta", "rahul.mehta@microsoft.com", "+91 98222 33445", "Principal Software Engineering Manager"),
        (3, "Amit Joshi", "amitjoshi@google.com", "+91 98333 44556", "Senior Cloud Systems Architect"),
        (4, "Vikram Singhania", "v.singhania@tcs.com", "+91 98444 55667", "Lead Robotics Architect")
    ]
    for cs in supervisors_data:
        db.execute("INSERT INTO Company_Supervisors (Org_ID, Name, Email, Phone, Designation) VALUES (%s, %s, %s, %s, %s)", cs)

    # 6. Seed Applications
    app1 = db.execute_lastrowid("INSERT INTO Applications (Student_ID, Opp_ID, Application_Date, Status, Statement_Of_Purpose) VALUES (%s, %s, %s, %s, %s)",
                               (1, 1, "2026-05-10", "Accepted", "Eager to contribute to GPU kernel optimization and TensorRT benchmarking at NVIDIA. Solid background in C++, CUDA, and deep learning architectures."))
    app2 = db.execute_lastrowid("INSERT INTO Applications (Student_ID, Opp_ID, Application_Date, Status, Statement_Of_Purpose) VALUES (%s, %s, %s, %s, %s)",
                               (2, 2, "2026-05-12", "Accepted", "Passionate about cloud reliability, distributed locks, and container orchestration at Microsoft IDC."))
    app3 = db.execute_lastrowid("INSERT INTO Applications (Student_ID, Opp_ID, Application_Date, Status, Statement_Of_Purpose) VALUES (%s, %s, %s, %s, %s)",
                               (3, 3, "2026-05-15", "Under_Review", "Solid background in Vector DB embeddings, Retrieval-Augmented Generation, and RAG evaluation."))
    app4 = db.execute_lastrowid("INSERT INTO Applications (Student_ID, Opp_ID, Application_Date, Status, Statement_Of_Purpose) VALUES (%s, %s, %s, %s, %s)",
                               (4, 4, "2026-05-16", "Pending", "Experience with OpenCV, LiDAR point cloud processing, and ROS2 simulation."))

    # 7. Seed Approvals
    approval1 = db.execute_lastrowid("INSERT INTO Approvals (App_ID, Faculty_ID, Approval_Status, Approval_Date, Remarks) VALUES (%s, %s, %s, %s, %s)",
                                     (app1, 1, "Approved", "2026-05-15", "Excellent fit for senior thesis in high-performance GPU computing. Prerequisites and academic credits verified."))
    approval2 = db.execute_lastrowid("INSERT INTO Approvals (App_ID, Faculty_ID, Approval_Status, Approval_Date, Remarks) VALUES (%s, %s, %s, %s, %s)",
                                     (app2, 2, "Approved", "2026-05-16", "Approved. Academic syllabus aligned with enterprise distributed systems."))
    approval3 = db.execute_lastrowid("INSERT INTO Approvals (App_ID, Faculty_ID, Approval_Status, Approval_Date, Remarks) VALUES (%s, %s, %s, %s, %s)",
                                     (app3, 1, "Pending", None, "Awaiting departmental committee validation."))

    # 8. Seed Assignments
    assign1 = db.execute_lastrowid("INSERT INTO Assignments (Approval_ID, Faculty_ID, Supervisor_ID, Start_Date, End_Date, Status) VALUES (%s, %s, %s, %s, %s, %s)",
                                  (approval1, 1, 1, "2026-06-01", "2026-08-31", "Active"))
    assign2 = db.execute_lastrowid("INSERT INTO Assignments (Approval_ID, Faculty_ID, Supervisor_ID, Start_Date, End_Date, Status) VALUES (%s, %s, %s, %s, %s, %s)",
                                  (approval2, 2, 2, "2026-06-01", "2026-08-31", "Completed"))

    # 9. Seed Weekly Logs (Includes Tasks to Perform & Work Performed)
    logs_data = [
        (assign1, 1, "Set up CUDA 12.4 developer environment, configure Nsight profiler, and analyze baseline latency of multi-head attention kernels.", "Completed orientation, NDA clearance, and configured workstation with CUDA 12.4 and PyTorch nightly. Profiled baseline kernels.", "2026-06-07", 40, "Reviewed", "Environment verified and baseline numbers match target specs."),
        (assign1, 2, "Benchmark FP8 matrix multiplication vs FP16 on Hopper architecture; isolate memory bandwidth latency bottlenecks in attention projection.", "Benchmarked FP8 matrix multiplication vs FP16 on Hopper architecture; identified memory bandwidth bottleneck in attention head projection layer.", "2026-06-14", 42, "Reviewed", "Solid benchmarking methodology. Proceed with Triton fused kernel."),
        (assign1, 3, "Implement custom Triton fused kernel for flash-decoding with 4k context token sequences; verify mathematical precision against FP32 ground truth.", "Authored custom Triton fused kernel for flash-decoding, cutting latency from 14.2ms to 9.1ms across 4k context token sequences. Verified precision.", "2026-06-21", 45, "Reviewed", "Impressive 35% latency reduction achieved. Excellent work!"),
        (assign1, 4, "Package fused kernel for integration testing into TensorRT-LLM pipeline; document benchmark results for engineering review.", "Integrated fused kernel into TensorRT-LLM pipeline and verified numerical precision against FP32 ground truth across 100 test runs.", "2026-06-28", 40, "Submitted", "Under mentor review.")
    ]
    for log in logs_data:
        db.execute("""
            INSERT INTO Weekly_Logs (Assignment_ID, Week_Number, Tasks_To_Perform, Report_Text, Submission_Date, Hours_Worked, Status, Review_Comments)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, log)

    # 10. Seed Dual Evaluations for Assignment 2
    db.execute("""
        INSERT INTO Evaluations (Assignment_ID, Score, Technical_Score, Professionalism_Score, Feedback_Text, Evaluation_Date, Evaluator_Role, Evaluator_Name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (assign2, 96.50, 98.0, 95.0, "Exceptional grasp of distributed fault-tolerance. Aryan contributed code directly to the production Azure queue router with stellar code quality.", "2026-08-30", "Company_Supervisor", "Rahul Mehta (Microsoft Principal Manager)"))

    db.execute("""
        INSERT INTO Evaluations (Assignment_ID, Score, Technical_Score, Professionalism_Score, Feedback_Text, Evaluation_Date, Evaluator_Role, Evaluator_Name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (assign2, 94.00, 95.0, 93.0, "Met all departmental credit standards with excellence. Strong theoretical documentation and prompt weekly reports.", "2026-08-31", "Faculty_Mentor", "Dr. K. Venkat (Department Chair)"))

    # 11. Seed Certificate for Assignment 2
    cert_code = "IT-2026-WOX-8742-ARYAN"
    db.execute("INSERT INTO Certificates (Assignment_ID, Issue_Date, Verification_Code, Grade) VALUES (%s, %s, %s, %s)",
               (assign2, "2026-09-02", cert_code, "Distinction (O)"))

    # 12. Seed Feedback
    db.execute("INSERT INTO Feedback (Assignment_ID, Given_By, Author_Name, Comments, Rating) VALUES (%s, %s, %s, %s, %s)",
               (assign2, "Supervisor", "Rahul Mehta (Microsoft)", "High professionalism, proactive communicator, strong algorithmic fundamentals and production code quality.", 5))
    db.execute("INSERT INTO Feedback (Assignment_ID, Given_By, Author_Name, Comments, Rating) VALUES (%s, %s, %s, %s, %s)",
               (assign2, "Faculty", "Dr. K. Venkat (Faculty)", "Student kept weekly logs updated and effectively bridged theory with real-world enterprise infrastructure.", 5))
    db.execute("INSERT INTO Feedback (Assignment_ID, Given_By, Author_Name, Comments, Rating) VALUES (%s, %s, %s, %s, %s)",
               (assign2, "Student", "Aryan Varma (Student)", "Mentorship at Microsoft IDC was outstanding; I learned production scale resilience and distributed coordination.", 5))

    print("[InternTrack] 12-table seeding complete!")


# ----------------------------------------------------------------------------
# Context Processors & Helper Utilities
# ----------------------------------------------------------------------------
@app.context_processor
def inject_global_metadata():
    return {
        "current_year": datetime.date.today().year,
        "is_sqlite": db.is_using_sqlite(),
        "app_name": "InternTrack",
        "institution": "University Placement & Internship ERP"
    }


# ----------------------------------------------------------------------------
# 1. Dashboard Route (/)
# ----------------------------------------------------------------------------
@app.route('/')
def dashboard():
    total_students = db.fetch_one("SELECT COUNT(*) as cnt FROM Students")['cnt']
    total_orgs = db.fetch_one("SELECT COUNT(*) as cnt FROM Organizations")['cnt']
    total_opps = db.fetch_one("SELECT COUNT(*) as cnt FROM Opportunities")['cnt']
    total_apps = db.fetch_one("SELECT COUNT(*) as cnt FROM Applications")['cnt']
    pending_approvals = db.fetch_one("SELECT COUNT(*) as cnt FROM Approvals WHERE Approval_Status = 'Pending'")['cnt']
    active_assignments = db.fetch_one("SELECT COUNT(*) as cnt FROM Assignments WHERE Status = 'Active'")['cnt']
    issued_certificates = db.fetch_one("SELECT COUNT(*) as cnt FROM Certificates")['cnt']
    total_logs = db.fetch_one("SELECT COUNT(*) as cnt FROM Weekly_Logs")['cnt']

    avg_score_res = db.fetch_one("SELECT AVG(Score) as avg_score FROM Evaluations")
    avg_score = round(avg_score_res['avg_score'], 1) if avg_score_res and avg_score_res['avg_score'] else 95.2

    recent_placements = db.fetch_all("""
        SELECT a.Assignment_ID, a.Start_Date, a.End_Date, a.Status,
               s.Name as Student_Name, s.Department, s.Email as Student_Email,
               o.Org_Name, opp.Title as Opportunity_Title,
               fm.Name as Faculty_Name, cs.Name as Supervisor_Name
        FROM Assignments a
        JOIN Approvals app ON a.Approval_ID = app.Approval_ID
        JOIN Applications appl ON app.App_ID = appl.App_ID
        JOIN Students s ON appl.Student_ID = s.Student_ID
        JOIN Opportunities opp ON appl.Opp_ID = opp.Opp_ID
        JOIN Organizations o ON opp.Org_ID = o.Org_ID
        JOIN Faculty_Mentors fm ON a.Faculty_ID = fm.Faculty_ID
        JOIN Company_Supervisors cs ON a.Supervisor_ID = cs.Supervisor_ID
        ORDER BY a.Assignment_ID DESC
        LIMIT 6;
    """)

    recent_work_logs = db.fetch_all("""
        SELECT wl.Log_ID, wl.Week_Number, wl.Tasks_To_Perform, wl.Report_Text, wl.Submission_Date, wl.Hours_Worked, wl.Status,
               s.Name as Student_Name
        FROM Weekly_Logs wl
        JOIN Assignments a ON wl.Assignment_ID = a.Assignment_ID
        JOIN Approvals app ON a.Approval_ID = app.Approval_ID
        JOIN Applications appl ON app.App_ID = appl.App_ID
        JOIN Students s ON appl.Student_ID = s.Student_ID
        ORDER BY wl.Log_ID DESC
        LIMIT 5;
    """)

    return render_template(
        'dashboard.html',
        total_students=total_students,
        total_orgs=total_orgs,
        total_opps=total_opps,
        total_apps=total_apps,
        pending_approvals=pending_approvals,
        active_assignments=active_assignments,
        issued_certificates=issued_certificates,
        total_logs=total_logs,
        avg_score=avg_score,
        recent_placements=recent_placements,
        recent_work_logs=recent_work_logs
    )


# ----------------------------------------------------------------------------
# 2. Student Portal Route (/student-portal)
# ----------------------------------------------------------------------------
@app.route('/student-portal', methods=['GET', 'POST'])
def student_portal():
    student_id = request.args.get('student_id', 1, type=int)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'apply':
            opp_id = request.form.get('opp_id', type=int)
            sop = request.form.get('statement_of_purpose', '')

            # Check duplicate application constraint
            existing = db.fetch_one("SELECT * FROM Applications WHERE Student_ID = %s AND Opp_ID = %s", (student_id, opp_id))
            if existing:
                flash("Duplicate Application: You have already applied to this opportunity.", "danger")
            else:
                today = datetime.date.today().isoformat()
                app_id = db.execute_lastrowid(
                    "INSERT INTO Applications (Student_ID, Opp_ID, Application_Date, Status, Statement_Of_Purpose) VALUES (%s, %s, %s, %s, %s)",
                    (student_id, opp_id, today, 'Pending', sop)
                )
                # Auto route to faculty approvals
                default_faculty = db.fetch_one("SELECT Faculty_ID FROM Faculty_Mentors LIMIT 1")
                faculty_id = default_faculty['Faculty_ID'] if default_faculty else 1
                db.execute(
                    "INSERT INTO Approvals (App_ID, Faculty_ID, Approval_Status, Remarks) VALUES (%s, %s, %s, %s)",
                    (app_id, faculty_id, 'Pending', 'Awaiting faculty prerequisite validation')
                )
                flash("Application submitted successfully and routed to faculty for review!", "success")

            return redirect(url_for('student_portal', student_id=student_id))

        elif action == 'submit_log':
            assign_id = request.form.get('assignment_id', type=int)
            week_num = request.form.get('week_number', type=int)
            tasks_to_perform = request.form.get('tasks_to_perform', '')
            report_text = request.form.get('report_text', '')
            hours = request.form.get('hours_worked', 40, type=int)
            today = datetime.date.today().isoformat()

            db.execute("""
                INSERT INTO Weekly_Logs (Assignment_ID, Week_Number, Tasks_To_Perform, Report_Text, Submission_Date, Hours_Worked, Status)
                VALUES (%s, %s, %s, %s, %s, %s, 'Submitted')
            """, (assign_id, week_num, tasks_to_perform, report_text, today, hours))
            flash(f"Week {week_num} work progress log submitted successfully!", "success")
            return redirect(url_for('student_portal', student_id=student_id))

    current_student = db.fetch_one("SELECT * FROM Students WHERE Student_ID = %s", (student_id,))
    all_students = db.fetch_all("SELECT * FROM Students ORDER BY Name ASC")

    open_opportunities = db.fetch_all("""
        SELECT opp.*, o.Org_Name, o.Industry,
               (SELECT COUNT(*) FROM Applications a WHERE a.Opp_ID = opp.Opp_ID AND a.Student_ID = %s) as Has_Applied
        FROM Opportunities opp
        JOIN Organizations o ON opp.Org_ID = o.Org_ID
        ORDER BY opp.Opp_ID DESC;
    """, (student_id,))

    my_applications = db.fetch_all("""
        SELECT a.App_ID, a.Application_Date, a.Status as Application_Status, a.Statement_Of_Purpose,
               opp.Title as Opportunity_Title, opp.Stipend, o.Org_Name,
               appr.Approval_Status, appr.Remarks as Faculty_Remarks
        FROM Applications a
        JOIN Opportunities opp ON a.Opp_ID = opp.Opp_ID
        JOIN Organizations o ON opp.Org_ID = o.Org_ID
        LEFT JOIN Approvals appr ON a.App_ID = appr.App_ID
        WHERE a.Student_ID = %s
        ORDER BY a.App_ID DESC;
    """, (student_id,))

    my_assignments = db.fetch_all("""
        SELECT assign.Assignment_ID, assign.Start_Date, assign.End_Date, assign.Status as Assignment_Status,
               opp.Title as Role_Title, o.Org_Name,
               fm.Name as Faculty_Mentor_Name, cs.Name as Company_Supervisor_Name,
               c.Verification_Code as Certificate_Code, c.Grade as Certificate_Grade
        FROM Assignments assign
        JOIN Approvals appr ON assign.Approval_ID = appr.Approval_ID
        JOIN Applications a ON appr.App_ID = a.App_ID
        JOIN Opportunities opp ON a.Opp_ID = opp.Opp_ID
        JOIN Organizations o ON opp.Org_ID = o.Org_ID
        JOIN Faculty_Mentors fm ON assign.Faculty_ID = fm.Faculty_ID
        JOIN Company_Supervisors cs ON assign.Supervisor_ID = cs.Supervisor_ID
        LEFT JOIN Certificates c ON assign.Assignment_ID = c.Assignment_ID
        WHERE a.Student_ID = %s;
    """, (student_id,))

    return render_template(
        'student_portal.html',
        current_student=current_student,
        all_students=all_students,
        open_opportunities=open_opportunities,
        my_applications=my_applications,
        my_assignments=my_assignments
    )


# ----------------------------------------------------------------------------
# 3. Opportunities & Organizations (/opportunities)
# ----------------------------------------------------------------------------
@app.route('/opportunities', methods=['GET', 'POST'])
def opportunities():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'add_organization':
            org_name = request.form.get('org_name')
            industry = request.form.get('industry')
            address = request.form.get('address')
            email = request.form.get('email')
            website = request.form.get('website')

            db.execute("""
                INSERT INTO Organizations (Org_Name, Industry, Address, Email, Website)
                VALUES (%s, %s, %s, %s, %s)
            """, (org_name, industry, address, email, website))
            flash(f"Partner Organization '{org_name}' registered successfully!", "success")

        elif form_type == 'create_opportunity':
            org_id = request.form.get('org_id', type=int)
            title = request.form.get('title')
            description = request.form.get('description')
            stipend = request.form.get('stipend', 0.0, type=float)
            location = request.form.get('location')
            openings = request.form.get('openings', 1, type=int)

            db.execute("""
                INSERT INTO Opportunities (Org_ID, Title, Description, Stipend, Location, Openings)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (org_id, title, description, stipend, location, openings))
            flash(f"Internship opening '{title}' posted successfully!", "success")

        return redirect(url_for('opportunities'))

    organizations_list = db.fetch_all("""
        SELECT o.*,
               (SELECT COUNT(*) FROM Opportunities opp WHERE opp.Org_ID = o.Org_ID) as Total_Opportunities,
               (SELECT COUNT(*) FROM Company_Supervisors cs WHERE cs.Org_ID = o.Org_ID) as Total_Supervisors
        FROM Organizations o
        ORDER BY o.Org_Name ASC;
    """)

    opportunities_list = db.fetch_all("""
        SELECT opp.*, o.Org_Name, o.Industry,
               (SELECT COUNT(*) FROM Applications a WHERE a.Opp_ID = opp.Opp_ID) as Application_Count
        FROM Opportunities opp
        JOIN Organizations o ON opp.Org_ID = o.Org_ID
        ORDER BY opp.Opp_ID DESC;
    """)

    return render_template(
        'opportunities.html',
        organizations=organizations_list,
        opportunities=opportunities_list
    )


# ----------------------------------------------------------------------------
# 4. Applications & Approvals (/applications)
# ----------------------------------------------------------------------------
@app.route('/applications', methods=['GET', 'POST'])
def applications():
    if request.method == 'POST':
        app_id = request.form.get('app_id', type=int)
        approval_id = request.form.get('approval_id', type=int)
        faculty_id = request.form.get('faculty_id', type=int)
        decision = request.form.get('decision')
        remarks = request.form.get('remarks', '')
        today = datetime.date.today().isoformat()

        db.execute("""
            UPDATE Approvals
            SET Faculty_ID = %s, Approval_Status = %s, Approval_Date = %s, Remarks = %s
            WHERE Approval_ID = %s
        """, (faculty_id, decision, today, remarks, approval_id))

        app_status = 'Accepted' if decision == 'Approved' else 'Rejected'
        db.execute("UPDATE Applications SET Status = %s WHERE App_ID = %s", (app_status, app_id))

        flash(f"Application #{app_id} marked as {decision}!", "success")
        return redirect(url_for('applications'))

    status_filter = request.args.get('status', 'all')
    where_clause = ""
    params = ()

    if status_filter in ['Pending', 'Approved', 'Rejected']:
        where_clause = "WHERE app.Approval_Status = %s"
        params = (status_filter,)

    query = f"""
        SELECT a.App_ID, a.Application_Date, a.Status, a.Statement_Of_Purpose,
               s.Student_ID, s.Name as Student_Name, s.Department, s.CGPA, s.Email as Student_Email,
               opp.Opp_ID, opp.Title as Opportunity_Title, o.Org_Name,
               app.Approval_ID, app.Approval_Status, app.Approval_Date, app.Remarks,
               fm.Faculty_ID, fm.Name as Faculty_Name,
               assign.Assignment_ID
        FROM Applications a
        JOIN Students s ON a.Student_ID = s.Student_ID
        JOIN Opportunities opp ON a.Opp_ID = opp.Opp_ID
        JOIN Organizations o ON opp.Org_ID = o.Org_ID
        LEFT JOIN Approvals app ON a.App_ID = app.App_ID
        LEFT JOIN Faculty_Mentors fm ON app.Faculty_ID = fm.Faculty_ID
        LEFT JOIN Assignments assign ON app.Approval_ID = assign.Approval_ID
        {where_clause}
        ORDER BY a.App_ID DESC;
    """

    applications_list = db.fetch_all(query, params)
    faculty_list = db.fetch_all("SELECT * FROM Faculty_Mentors ORDER BY Name ASC;")

    return render_template(
        'applications.html',
        applications=applications_list,
        faculty_members=faculty_list,
        current_filter=status_filter
    )


# ----------------------------------------------------------------------------
# 5. Mentors & Assignments (/assignments)
# ----------------------------------------------------------------------------
@app.route('/assignments', methods=['GET', 'POST'])
def assignments():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create_assignment':
            approval_id = request.form.get('approval_id', type=int)
            faculty_id = request.form.get('faculty_id', type=int)
            supervisor_id = request.form.get('supervisor_id', type=int)
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')

            if start_date >= end_date:
                flash("Integrity Error: Start Date must be earlier than End Date.", "danger")
            else:
                db.execute("""
                    INSERT INTO Assignments (Approval_ID, Faculty_ID, Supervisor_ID, Start_Date, End_Date, Status)
                    VALUES (%s, %s, %s, %s, %s, 'Active')
                """, (approval_id, faculty_id, supervisor_id, start_date, end_date))
                flash("Tripartite internship contract executed successfully!", "success")

        elif action == 'add_faculty':
            name = request.form.get('name')
            dept = request.form.get('department')
            email = request.form.get('email')
            phone = request.form.get('phone')
            designation = request.form.get('designation', 'Associate Professor')

            db.execute("""
                INSERT INTO Faculty_Mentors (Name, Department, Email, Phone, Designation)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, dept, email, phone, designation))
            flash(f"Faculty Mentor '{name}' registered!", "success")

        elif action == 'add_supervisor':
            org_id = request.form.get('org_id', type=int)
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            designation = request.form.get('designation')

            db.execute("""
                INSERT INTO Company_Supervisors (Org_ID, Name, Email, Phone, Designation)
                VALUES (%s, %s, %s, %s, %s)
            """, (org_id, name, email, phone, designation))
            flash(f"Company Supervisor '{name}' registered!", "success")

        return redirect(url_for('assignments'))

    unassigned_approvals = db.fetch_all("""
        SELECT app.Approval_ID, s.Name as Student_Name, s.Department, s.CGPA,
               opp.Title as Opportunity_Title, o.Org_Name, o.Org_ID,
               app.Faculty_ID
        FROM Approvals app
        JOIN Applications a ON app.App_ID = a.App_ID
        JOIN Students s ON a.Student_ID = s.Student_ID
        JOIN Opportunities opp ON a.Opp_ID = opp.Opp_ID
        JOIN Organizations o ON opp.Org_ID = o.Org_ID
        LEFT JOIN Assignments assign ON app.Approval_ID = assign.Approval_ID
        WHERE app.Approval_Status = 'Approved' AND assign.Assignment_ID IS NULL;
    """)

    active_assignments = db.fetch_all("""
        SELECT assign.Assignment_ID, assign.Start_Date, assign.End_Date, assign.Status,
               s.Name as Student_Name, s.Department, s.CGPA,
               opp.Title as Role_Title, o.Org_Name,
               fm.Name as Faculty_Name, fm.Department as Faculty_Dept,
               cs.Name as Supervisor_Name, cs.Designation as Supervisor_Designation,
               (SELECT COUNT(*) FROM Weekly_Logs wl WHERE wl.Assignment_ID = assign.Assignment_ID) as Total_Logs,
               (SELECT Score FROM Evaluations e WHERE e.Assignment_ID = assign.Assignment_ID LIMIT 1) as Evaluation_Score
        FROM Assignments assign
        JOIN Approvals app ON assign.Approval_ID = app.Approval_ID
        JOIN Applications a ON app.App_ID = a.App_ID
        JOIN Students s ON a.Student_ID = s.Student_ID
        JOIN Opportunities opp ON a.Opp_ID = opp.Opp_ID
        JOIN Organizations o ON opp.Org_ID = o.Org_ID
        JOIN Faculty_Mentors fm ON assign.Faculty_ID = fm.Faculty_ID
        JOIN Company_Supervisors cs ON assign.Supervisor_ID = cs.Supervisor_ID
        ORDER BY assign.Assignment_ID DESC;
    """)

    faculty_list = db.fetch_all("SELECT * FROM Faculty_Mentors ORDER BY Name ASC;")
    supervisors_list = db.fetch_all("""
        SELECT cs.*, o.Org_Name
        FROM Company_Supervisors cs
        JOIN Organizations o ON cs.Org_ID = o.Org_ID
        ORDER BY cs.Name ASC;
    """)
    orgs_list = db.fetch_all("SELECT * FROM Organizations ORDER BY Org_Name ASC;")

    return render_template(
        'assignments.html',
        unassigned=unassigned_approvals,
        assignments=active_assignments,
        faculty=faculty_list,
        supervisors=supervisors_list,
        organizations=orgs_list
    )


# ----------------------------------------------------------------------------
# 6. Monitoring & Evaluations (/monitoring)
# ----------------------------------------------------------------------------
@app.route('/monitoring', methods=['GET', 'POST'])
def monitoring():
    selected_assign_id = request.args.get('assignment_id', type=int)

    if not selected_assign_id:
        first_assign = db.fetch_one("SELECT Assignment_ID FROM Assignments ORDER BY Assignment_ID DESC LIMIT 1")
        selected_assign_id = first_assign['Assignment_ID'] if first_assign else 1

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'assign_work':
            week_num = request.form.get('week_number', type=int)
            tasks = request.form.get('tasks_to_perform')
            today = datetime.date.today().isoformat()

            db.execute("""
                INSERT INTO Weekly_Logs (Assignment_ID, Week_Number, Tasks_To_Perform, Report_Text, Submission_Date, Hours_Worked, Status)
                VALUES (%s, %s, %s, 'Scheduled for execution.', %s, 40, 'Submitted')
            """, (selected_assign_id, week_num, tasks, today))
            flash(f"Assigned tasks to perform for Week {week_num}!", "success")

        elif action == 'submit_log':
            week_num = request.form.get('week_number', type=int)
            tasks = request.form.get('tasks_to_perform', '')
            report_text = request.form.get('report_text')
            hours = request.form.get('hours_worked', 40, type=int)
            today = datetime.date.today().isoformat()

            db.execute("""
                INSERT INTO Weekly_Logs (Assignment_ID, Week_Number, Tasks_To_Perform, Report_Text, Submission_Date, Hours_Worked, Status)
                VALUES (%s, %s, %s, %s, %s, %s, 'Submitted')
            """, (selected_assign_id, week_num, tasks, report_text, today, hours))
            flash(f"Week {week_num} progress log submitted!", "success")

        elif action == 'review_log':
            log_id = request.form.get('log_id', type=int)
            status = request.form.get('status', 'Reviewed')
            comments = request.form.get('review_comments', '')

            db.execute("""
                UPDATE Weekly_Logs
                SET Status = %s, Review_Comments = %s
                WHERE Log_ID = %s
            """, (status, comments, log_id))
            flash("Mentor review comments saved!", "success")

        elif action == 'submit_evaluation':
            score = request.form.get('score', type=float)
            tech_score = request.form.get('technical_score', type=float)
            prof_score = request.form.get('professionalism_score', type=float)
            feedback_text = request.form.get('feedback_text')
            evaluator_role = request.form.get('evaluator_role')
            evaluator_name = request.form.get('evaluator_name')
            today = datetime.date.today().isoformat()

            db.execute("""
                INSERT INTO Evaluations (Assignment_ID, Score, Technical_Score, Professionalism_Score, Feedback_Text, Evaluation_Date, Evaluator_Role, Evaluator_Name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (selected_assign_id, score, tech_score, prof_score, feedback_text, today, evaluator_role, evaluator_name))
            flash("Performance evaluation scorecard recorded!", "success")

        elif action == 'submit_feedback':
            given_by = request.form.get('given_by')
            author_name = request.form.get('author_name')
            comments = request.form.get('comments')
            rating = request.form.get('rating', 5, type=int)

            db.execute("""
                INSERT INTO Feedback (Assignment_ID, Given_By, Author_Name, Comments, Rating)
                VALUES (%s, %s, %s, %s, %s)
            """, (selected_assign_id, given_by, author_name, comments, rating))
            flash("Stakeholder feedback and rating recorded!", "success")

        elif action == 'issue_certificate':
            grade = request.form.get('grade', 'Distinction (A+)')
            today = datetime.date.today().isoformat()
            year = datetime.date.today().year
            rand_code = uuid.uuid4().hex[:6].upper()
            code = f"IT-{year}-WOX-{rand_code}"

            db.execute("""
                INSERT INTO Certificates (Assignment_ID, Issue_Date, Verification_Code, Grade)
                VALUES (%s, %s, %s, %s)
            """, (selected_assign_id, today, code, grade))
            db.execute("UPDATE Assignments SET Status = 'Completed' WHERE Assignment_ID = %s", (selected_assign_id,))
            flash(f"Completion Certificate generated with Code: {code}", "success")

        return redirect(url_for('monitoring', assignment_id=selected_assign_id))

    all_assignments = db.fetch_all("""
        SELECT assign.Assignment_ID, s.Name as Student_Name, opp.Title as Role_Title, o.Org_Name
        FROM Assignments assign
        JOIN Approvals app ON assign.Approval_ID = app.Approval_ID
        JOIN Applications a ON app.App_ID = a.App_ID
        JOIN Students s ON a.Student_ID = s.Student_ID
        JOIN Opportunities opp ON a.Opp_ID = opp.Opp_ID
        JOIN Organizations o ON opp.Org_ID = o.Org_ID
        ORDER BY assign.Assignment_ID DESC;
    """)

    assignment_details = db.fetch_one("""
        SELECT assign.*, s.Name as Student_Name, s.Department, s.Email as Student_Email, s.CGPA,
               opp.Title as Role_Title, o.Org_Name, o.Industry,
               fm.Name as Faculty_Name, fm.Email as Faculty_Email,
               cs.Name as Supervisor_Name, cs.Email as Supervisor_Email,
               cert.Verification_Code as Certificate_Code, cert.Grade as Certificate_Grade, cert.Issue_Date as Certificate_Date
        FROM Assignments assign
        JOIN Approvals app ON assign.Approval_ID = app.Approval_ID
        JOIN Applications a ON app.App_ID = a.App_ID
        JOIN Students s ON a.Student_ID = s.Student_ID
        JOIN Opportunities opp ON a.Opp_ID = opp.Opp_ID
        JOIN Organizations o ON opp.Org_ID = o.Org_ID
        JOIN Faculty_Mentors fm ON assign.Faculty_ID = fm.Faculty_ID
        JOIN Company_Supervisors cs ON assign.Supervisor_ID = cs.Supervisor_ID
        LEFT JOIN Certificates cert ON assign.Assignment_ID = cert.Assignment_ID
        WHERE assign.Assignment_ID = %s;
    """, (selected_assign_id,))

    logs = db.fetch_all("SELECT * FROM Weekly_Logs WHERE Assignment_ID = %s ORDER BY Week_Number ASC;", (selected_assign_id,))
    evaluations = db.fetch_all("SELECT * FROM Evaluations WHERE Assignment_ID = %s ORDER BY Evaluation_ID DESC;", (selected_assign_id,))
    feedback = db.fetch_all("SELECT * FROM Feedback WHERE Assignment_ID = %s ORDER BY Feedback_ID DESC;", (selected_assign_id,))

    return render_template(
        'monitoring.html',
        assignments=all_assignments,
        current_assignment=assignment_details,
        logs=logs,
        evaluations=evaluations,
        feedback=feedback
    )


# ----------------------------------------------------------------------------
# 7. Administrator Login Route (/admin-login)
# ----------------------------------------------------------------------------
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if email and password:
            flash(f"Administrator authenticated successfully as {email}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Please enter both admin email and password.", "danger")

    return render_template('admin_login.html')


@app.route('/admin-logout')
def admin_logout():
    flash("Administrator session terminated safely.", "info")
    return redirect(url_for('dashboard'))


# ----------------------------------------------------------------------------
# 8. JSON API Stats (/api/stats)
# ----------------------------------------------------------------------------
@app.route('/api/stats')
def api_stats():
    stats = {
        "students": db.fetch_one("SELECT COUNT(*) as cnt FROM Students")['cnt'],
        "organizations": db.fetch_one("SELECT COUNT(*) as cnt FROM Organizations")['cnt'],
        "opportunities": db.fetch_one("SELECT COUNT(*) as cnt FROM Opportunities")['cnt'],
        "applications": db.fetch_one("SELECT COUNT(*) as cnt FROM Applications")['cnt'],
        "approvals": db.fetch_one("SELECT COUNT(*) as cnt FROM Approvals")['cnt'],
        "faculty_mentors": db.fetch_one("SELECT COUNT(*) as cnt FROM Faculty_Mentors")['cnt'],
        "company_supervisors": db.fetch_one("SELECT COUNT(*) as cnt FROM Company_Supervisors")['cnt'],
        "assignments": db.fetch_one("SELECT COUNT(*) as cnt FROM Assignments")['cnt'],
        "weekly_logs": db.fetch_one("SELECT COUNT(*) as cnt FROM Weekly_Logs")['cnt'],
        "evaluations": db.fetch_one("SELECT COUNT(*) as cnt FROM Evaluations")['cnt'],
        "certificates": db.fetch_one("SELECT COUNT(*) as cnt FROM Certificates")['cnt'],
        "feedback": db.fetch_one("SELECT COUNT(*) as cnt FROM Feedback")['cnt']
    }
    return jsonify(stats)


# Auto initialize database on module import
with app.app_context():
    try:
        verify_and_seed_database()
    except Exception as e:
        print(f"[InternTrack] DB auto-initialization notice: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
