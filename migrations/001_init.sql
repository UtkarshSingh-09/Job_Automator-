-- ==============================================================================
-- Migration 001: Initial Core Schema
-- Defines: profile, projects, companies, jobs, matches, applications, run_log
-- ==============================================================================

-- 1. Profile Table (Single user row, enforced id=1)
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    github_url TEXT,
    linkedin_url TEXT,
    portfolio_url TEXT,
    college TEXT,
    degree TEXT,
    branch TEXT,
    grad_year INTEGER,
    cgpa REAL,
    location TEXT,
    skills_json TEXT NOT NULL DEFAULT '[]',
    coursework_json TEXT NOT NULL DEFAULT '[]',
    achievements_json TEXT NOT NULL DEFAULT '[]',
    certifications_json TEXT NOT NULL DEFAULT '[]',
    raw_text TEXT,
    confirmed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Projects Table (Grounding knowledge corpus)
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_name TEXT UNIQUE NOT NULL,
    display_name TEXT,
    description TEXT,
    readme_md TEXT,
    manual_notes TEXT,
    languages_json TEXT DEFAULT '[]',
    primary_language TEXT,
    topics_json TEXT DEFAULT '[]',
    stars INTEGER DEFAULT 0,
    commit_count INTEGER DEFAULT 0,
    has_tests BOOLEAN DEFAULT 0,
    has_ci BOOLEAN DEFAULT 0,
    has_docker BOOLEAN DEFAULT 0,
    line_count INTEGER DEFAULT 0,
    quality_score REAL DEFAULT 0.0,
    include_override BOOLEAN DEFAULT 0,
    priority INTEGER DEFAULT 10,
    embedding BLOB,
    embedding_source_hash TEXT,
    created_at TIMESTAMP,
    pushed_at TIMESTAMP,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Companies Table (ATS detection and tracking)
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    domain TEXT UNIQUE NOT NULL,
    tier INTEGER DEFAULT 2,
    ats_provider TEXT,
    ats_slug TEXT,
    detection_status TEXT DEFAULT 'unknown', -- resolved | unknown | manual | dead
    etag TEXT,
    last_polled_at TIMESTAMP,
    consecutive_failures INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (ats_provider, ats_slug)
);

-- 4. Jobs Table (Ingested job listings)
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL,
    company_name TEXT NOT NULL,
    title TEXT NOT NULL,
    location TEXT,
    remote_type TEXT,
    description_md TEXT NOT NULL,
    apply_url TEXT NOT NULL,
    posted_at TIMESTAMP,
    source TEXT NOT NULL,
    source_job_id TEXT,
    content_hash TEXT UNIQUE NOT NULL,
    passed_filter BOOLEAN DEFAULT 0,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Matches Table (Semantic project selection and resume outputs)
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    overall_fit REAL,
    selected_projects_json TEXT DEFAULT '[]',
    selection_reasoning TEXT,
    uncovered_requirements_json TEXT DEFAULT '[]',
    bullets_json TEXT DEFAULT '[]',
    pdf_path TEXT,
    parse_ok BOOLEAN DEFAULT 0,
    coverage_score REAL DEFAULT 0.0,
    missing_terms_json TEXT DEFAULT '[]',
    attempts INTEGER DEFAULT 0,
    needs_review BOOLEAN DEFAULT 0,
    llm_cost_usd REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (job_id)
);

-- 6. Applications Table (Submission status, screenshot evidence)
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER REFERENCES matches(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'generated', -- generated | submitted | applied | rejected | interview
    auto_apply_status TEXT DEFAULT 'pending', -- pending | submitted | needs_login | captcha_blocked | form_error | skipped
    confirmation_screenshot TEXT,
    submit_attempted_at TIMESTAMP,
    applied_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Run Log Table (Execution heartbeat and pipeline statistics)
CREATE TABLE IF NOT EXISTS run_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_type TEXT NOT NULL, -- daily | fetch | match | generate | apply
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    status TEXT NOT NULL, -- success | partial | failure
    stats_json TEXT DEFAULT '{}',
    error TEXT
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_jobs_content_hash ON jobs(content_hash);
CREATE INDEX IF NOT EXISTS idx_jobs_passed_filter ON jobs(passed_filter);
CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies(domain);
CREATE INDEX IF NOT EXISTS idx_companies_ats ON companies(ats_provider, ats_slug);
CREATE INDEX IF NOT EXISTS idx_matches_job_id ON matches(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_match_id ON applications(match_id);
