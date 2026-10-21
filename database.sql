-- AI Resume Analyzer Relational Database Schema
-- Compatible with MySQL 8.0+ and SQLite

CREATE DATABASE IF NOT EXISTS resume_analyzer_db;
USE resume_analyzer_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Resumes Table
CREATE TABLE IF NOT EXISTS resumes (
    resume_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    filename VARCHAR(255) NOT NULL,
    raw_text LONGTEXT NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Job Roles Table
CREATE TABLE IF NOT EXISTS job_roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT NOT NULL
);

-- 4. Skills Taxonomy Table
CREATE TABLE IF NOT EXISTS skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) UNIQUE,
    category VARCHAR(50) NOT NULL
);

-- 5. Analyses Table
CREATE TABLE IF NOT EXISTS analyses (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    resume_id INT,
    target_role VARCHAR(100) NOT NULL,
    match_score INT NOT NULL,
    tfidf_score INT NOT NULL,
    section_score INT NOT NULL,
    detected_skills TEXT,
    missing_skills TEXT,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id) ON DELETE SET NULL
);

