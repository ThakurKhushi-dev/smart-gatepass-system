-- =============================================================
-- Smart Gatepass System v2 – MySQL Schema
-- Run once: mysql -u root -p < database/schema.sql
-- =============================================================

CREATE DATABASE IF NOT EXISTS gatepass_db;
USE gatepass_db;

-- =============================================================
-- DROP OLD TABLES (clean slate on re-run)
-- =============================================================
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS approvals;
DROP TABLE IF EXISTS requests;
DROP TABLE IF EXISTS users;

-- =============================================================
-- USERS TABLE
-- role: student | incharge | hod | warden | guard
-- student_type: day_scholar | hosteller  (NULL for authorities)
-- =============================================================
CREATE TABLE users (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    email        VARCHAR(100) UNIQUE NOT NULL,
    password     VARCHAR(255) NOT NULL,
    role         VARCHAR(50)  NOT NULL,
    department   VARCHAR(100),
    semester     INT,
    student_type VARCHAR(20),           -- day_scholar | hosteller
    phone        VARCHAR(15),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================
-- REQUESTS TABLE
-- REMOVED: is_emergency (feature removed completely)
-- ADDED  : request_subtype, out_date, return_date, return_time
--          approval_stage
-- =============================================================
CREATE TABLE requests (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT          NOT NULL,
    -- Denormalised snapshot of student info at submission time
    student_name    VARCHAR(100) NOT NULL,
    student_email   VARCHAR(100) NOT NULL,
    department      VARCHAR(100) NOT NULL,
    semester        INT          NOT NULL,
    student_type    VARCHAR(20)  NOT NULL,   -- day_scholar | hosteller

    reason          TEXT         NOT NULL,
    parent_phone    VARCHAR(15)  NOT NULL,

    -- "outing" | "leave" | "" (day scholars have no subtype)
    request_subtype VARCHAR(20)  DEFAULT '',

    -- Time / date fields
    out_time        VARCHAR(20),             -- e.g. "10:30 AM"
    in_time         VARCHAR(20),             -- e.g. "04:00 PM" – optional for day scholar leaving only
    out_date        VARCHAR(20),             -- YYYY-MM-DD – hosteller leave departure date
    return_date     VARCHAR(20),             -- YYYY-MM-DD – hosteller leave return date
    return_time     VARCHAR(20),             -- e.g. "06:00 PM" – hosteller leave return time

    -- Approval tracking
    -- status: pending | approved_by_incharge | approved_by_hod |
    --         approved_by_warden | fully_approved | rejected
    status          VARCHAR(50)  DEFAULT 'pending',
    -- approval_stage: which role must act next
    -- values: incharge | hod | warden | warden_only | done | rejected
    approval_stage  VARCHAR(50)  DEFAULT 'incharge',

    -- Gate tracking
    exit_marked     BOOLEAN      DEFAULT FALSE,
    entry_marked    BOOLEAN      DEFAULT FALSE,
    exit_time       TIMESTAMP    NULL,
    entry_time      TIMESTAMP    NULL,

    -- QR code: base64 PNG string, NULL until status = fully_approved
    qr_code         LONGTEXT,

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- =============================================================
-- APPROVALS TABLE
-- =============================================================
CREATE TABLE approvals (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    request_id    INT          NOT NULL,
    approver_id   INT          NOT NULL,
    approver_role VARCHAR(50)  NOT NULL,     -- incharge | hod | warden
    action        VARCHAR(20)  NOT NULL,     -- approved | rejected
    comments      TEXT,
    approved_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id)  REFERENCES requests(id),
    FOREIGN KEY (approver_id) REFERENCES users(id)
);

-- =============================================================
-- LOGS TABLE
-- =============================================================
CREATE TABLE logs (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT,
    user_id    INT,
    action     VARCHAR(255) NOT NULL,
    details    TEXT,
    logged_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES requests(id),
    FOREIGN KEY (user_id)    REFERENCES users(id)
);

-- =============================================================
-- ATTENDANCE TABLE
-- =============================================================
CREATE TABLE attendance (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    student_id       INT          NOT NULL,
    subject          VARCHAR(100) NOT NULL,
    total_classes    INT DEFAULT 0,
    attended_classes INT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- =============================================================
-- PRE-SEEDED AUTHORITY ACCOUNTS
-- Password for ALL accounts: password123
--
-- To generate a fresh hash yourself:
--   python -c "from passlib.context import CryptContext; \
--              ctx=CryptContext(schemes=['bcrypt']); \
--              print(ctx.hash('password123'))"
--
-- The hash below is a valid bcrypt hash for "password123"
-- =============================================================
INSERT INTO users (name, email, password, role, department, semester, student_type, phone) VALUES
('Prof. Meera Nair', 'incharge@college.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMH9M8V/pR8hZm5L9J2EaKvF5a',
 'incharge', 'Computer Science', NULL, NULL, '9876540001'),

('Dr. Suresh Kumar', 'hod@college.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMH9M8V/pR8hZm5L9J2EaKvF5a',
 'hod', 'Computer Science', NULL, NULL, '9876540002'),

('Mr. Ravi Shankar', 'warden@college.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMH9M8V/pR8hZm5L9J2EaKvF5a',
 'warden', NULL, NULL, NULL, '9876540003'),

('Guard Mohan', 'guard@college.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMH9M8V/pR8hZm5L9J2EaKvF5a',
 'guard', NULL, NULL, NULL, '9876540004');

-- =============================================================
-- NOTE: Students are NOT seeded here.
-- Students self-register via the Sign Up page.
-- =============================================================

-- =============================================================
-- OPTIONAL: Sample students for testing
-- Uncomment the block below if you want demo student accounts.
-- =============================================================
/*
INSERT INTO users (name, email, password, role, department, semester, student_type, phone) VALUES
('Arjun Sharma', 'arjun@student.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMH9M8V/pR8hZm5L9J2EaKvF5a',
 'student', 'Computer Science', 3, 'day_scholar', '9876543210'),

('Priya Patel', 'priya@student.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMH9M8V/pR8hZm5L9J2EaKvF5a',
 'student', 'Computer Science', 3, 'hosteller', '9876543211');

INSERT INTO attendance (student_id, subject, total_classes, attended_classes) VALUES
(5, 'Data Structures',   40, 35),
(5, 'Operating Systems', 38, 30),
(5, 'DBMS',              42, 40),
(6, 'Data Structures',   40, 38),
(6, 'DBMS',              42, 39);
*/
