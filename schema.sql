-- ============================================================================
-- InternTrack: 3NF Normalized Relational Database Schema (MySQL 8.0+)
-- University Internship Application & Progress Monitoring System
-- Exactly 12 Normalized Relational Tables (Strict 3NF Compliance)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS `interntrack` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `interntrack`;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `Feedback`;
DROP TABLE IF EXISTS `Certificates`;
DROP TABLE IF EXISTS `Evaluations`;
DROP TABLE IF EXISTS `Weekly_Logs`;
DROP TABLE IF EXISTS `Assignments`;
DROP TABLE IF EXISTS `Approvals`;
DROP TABLE IF EXISTS `Company_Supervisors`;
DROP TABLE IF EXISTS `Faculty_Mentors`;
DROP TABLE IF EXISTS `Applications`;
DROP TABLE IF EXISTS `Opportunities`;
DROP TABLE IF EXISTS `Organizations`;
DROP TABLE IF EXISTS `Students`;

SET FOREIGN_KEY_CHECKS = 1;

-- 1. Students Table
CREATE TABLE `Students` (
    `Student_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `Name` VARCHAR(100) NOT NULL,
    `Department` VARCHAR(100) NOT NULL,
    `Email` VARCHAR(150) NOT NULL UNIQUE,
    `Phone` VARCHAR(25) NOT NULL,
    `CGPA` DECIMAL(3,2) DEFAULT 8.50,
    `Created_At` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Organizations Table
CREATE TABLE `Organizations` (
    `Org_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `Org_Name` VARCHAR(150) NOT NULL,
    `Industry` VARCHAR(100) NOT NULL,
    `Address` VARCHAR(255) NOT NULL,
    `Email` VARCHAR(150) NOT NULL UNIQUE,
    `Website` VARCHAR(150) DEFAULT NULL,
    `Created_At` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. Opportunities Table (Posts Put Up by Partner Companies)
CREATE TABLE `Opportunities` (
    `Opp_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `Org_ID` INT NOT NULL,
    `Title` VARCHAR(150) NOT NULL,
    `Description` TEXT NOT NULL,
    `Stipend` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `Location` VARCHAR(100) NOT NULL,
    `Openings` INT NOT NULL DEFAULT 1,
    `Created_At` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_opp_org` FOREIGN KEY (`Org_ID`)
        REFERENCES `Organizations` (`Org_ID`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 4. Faculty_Mentors Table
CREATE TABLE `Faculty_Mentors` (
    `Faculty_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `Name` VARCHAR(100) NOT NULL,
    `Department` VARCHAR(100) NOT NULL,
    `Email` VARCHAR(150) NOT NULL UNIQUE,
    `Phone` VARCHAR(25) NOT NULL,
    `Designation` VARCHAR(100) DEFAULT 'Associate Professor'
) ENGINE=InnoDB;

-- 5. Company_Supervisors Table
CREATE TABLE `Company_Supervisors` (
    `Supervisor_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `Org_ID` INT NOT NULL,
    `Name` VARCHAR(100) NOT NULL,
    `Email` VARCHAR(150) NOT NULL,
    `Phone` VARCHAR(25) NOT NULL,
    `Designation` VARCHAR(100) NOT NULL,
    CONSTRAINT `fk_supervisor_org` FOREIGN KEY (`Org_ID`)
        REFERENCES `Organizations` (`Org_ID`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 6. Applications Table (Students Apply with Statement of Purpose)
CREATE TABLE `Applications` (
    `App_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `Student_ID` INT NOT NULL,
    `Opp_ID` INT NOT NULL,
    `Application_Date` DATE NOT NULL,
    `Status` ENUM('Pending', 'Under_Review', 'Accepted', 'Rejected') NOT NULL DEFAULT 'Pending',
    `Statement_Of_Purpose` TEXT DEFAULT NULL,
    CONSTRAINT `fk_app_student` FOREIGN KEY (`Student_ID`)
        REFERENCES `Students` (`Student_ID`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `fk_app_opportunity` FOREIGN KEY (`Opp_ID`)
        REFERENCES `Opportunities` (`Opp_ID`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `uq_student_opportunity` UNIQUE (`Student_ID`, `Opp_ID`)
) ENGINE=InnoDB;

-- 7. Approvals Table (Faculty Mentors Verify Prerequisites & Approve)
CREATE TABLE `Approvals` (
    `Approval_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `App_ID` INT NOT NULL UNIQUE,
    `Faculty_ID` INT NOT NULL,
    `Approval_Status` ENUM('Pending', 'Approved', 'Rejected') NOT NULL DEFAULT 'Pending',
    `Approval_Date` DATE DEFAULT NULL,
    `Remarks` TEXT DEFAULT NULL,
    CONSTRAINT `fk_approval_app` FOREIGN KEY (`App_ID`)
        REFERENCES `Applications` (`App_ID`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `fk_approval_faculty` FOREIGN KEY (`Faculty_ID`)
        REFERENCES `Faculty_Mentors` (`Faculty_ID`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 8. Assignments Table (Tripartite Binding: Student + Faculty Mentor + Company Supervisor)
CREATE TABLE `Assignments` (
    `Assignment_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `Approval_ID` INT NOT NULL UNIQUE,
    `Faculty_ID` INT NOT NULL,
    `Supervisor_ID` INT NOT NULL,
    `Start_Date` DATE NOT NULL,
    `End_Date` DATE NOT NULL,
    `Status` ENUM('Active', 'Completed', 'Terminated') NOT NULL DEFAULT 'Active',
    CONSTRAINT `fk_assignment_approval` FOREIGN KEY (`Approval_ID`)
        REFERENCES `Approvals` (`Approval_ID`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `fk_assignment_faculty` FOREIGN KEY (`Faculty_ID`)
        REFERENCES `Faculty_Mentors` (`Faculty_ID`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT `fk_assignment_supervisor` FOREIGN KEY (`Supervisor_ID`)
        REFERENCES `Company_Supervisors` (`Supervisor_ID`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 9. Weekly_Logs Table (Daily Work to Perform, Progress Deliverables & Review)
CREATE TABLE `Weekly_Logs` (
    `Log_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `Assignment_ID` INT NOT NULL,
    `Week_Number` INT NOT NULL,
    `Tasks_To_Perform` TEXT NOT NULL,
    `Report_Text` TEXT NOT NULL,
    `Submission_Date` DATE NOT NULL,
    `Hours_Worked` INT NOT NULL DEFAULT 40,
    `Status` ENUM('Submitted', 'Reviewed', 'Flagged') DEFAULT 'Submitted',
    `Review_Comments` TEXT DEFAULT NULL,
    CONSTRAINT `fk_log_assignment` FOREIGN KEY (`Assignment_ID`)
        REFERENCES `Assignments` (`Assignment_ID`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `uq_assignment_week` UNIQUE (`Assignment_ID`, `Week_Number`)
) ENGINE=InnoDB;

-- 10. Evaluations Table (Dual Evaluation: Scores from Faculty Mentor & Company Supervisor)
CREATE TABLE `Evaluations` (
    `Evaluation_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `Assignment_ID` INT NOT NULL,
    `Score` DECIMAL(5, 2) NOT NULL,
    `Technical_Score` DECIMAL(5, 2) DEFAULT 95.0,
    `Professionalism_Score` DECIMAL(5, 2) DEFAULT 95.0,
    `Feedback_Text` TEXT NOT NULL,
    `Evaluation_Date` DATE NOT NULL,
    `Evaluator_Role` ENUM('Company_Supervisor', 'Faculty_Mentor', 'Joint') DEFAULT 'Company_Supervisor',
    `Evaluator_Name` VARCHAR(100) DEFAULT NULL,
    CONSTRAINT `fk_eval_assignment` FOREIGN KEY (`Assignment_ID`)
        REFERENCES `Assignments` (`Assignment_ID`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 11. Certificates Table (Internship Completion Credentials)
CREATE TABLE `Certificates` (
    `Cert_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `Assignment_ID` INT NOT NULL UNIQUE,
    `Issue_Date` DATE NOT NULL,
    `Verification_Code` VARCHAR(64) NOT NULL UNIQUE,
    `Grade` VARCHAR(50) DEFAULT 'Distinction (A+)',
    CONSTRAINT `fk_cert_assignment` FOREIGN KEY (`Assignment_ID`)
        REFERENCES `Assignments` (`Assignment_ID`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 12. Feedback Table (360-Degree Ratings & Reviews by Stakeholders)
CREATE TABLE `Feedback` (
    `Feedback_ID` INT AUTO_INCREMENT PRIMARY KEY,
    `Assignment_ID` INT NOT NULL,
    `Given_By` ENUM('Student', 'Faculty', 'Supervisor', 'Admin') NOT NULL,
    `Author_Name` VARCHAR(100) NOT NULL,
    `Comments` TEXT NOT NULL,
    `Rating` INT DEFAULT 5,
    `Created_At` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_feedback_assignment` FOREIGN KEY (`Assignment_ID`)
        REFERENCES `Assignments` (`Assignment_ID`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Performance Indexes
CREATE INDEX `idx_app_student_status` ON `Applications` (`Student_ID`, `Status`);
CREATE INDEX `idx_assignment_dates` ON `Assignments` (`Start_Date`, `End_Date`);
CREATE INDEX `idx_logs_assignment` ON `Weekly_Logs` (`Assignment_ID`, `Week_Number`);
CREATE INDEX `idx_eval_assignment` ON `Evaluations` (`Assignment_ID`, `Evaluator_Role`);
