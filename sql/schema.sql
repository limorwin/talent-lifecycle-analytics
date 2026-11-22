CREATE TABLE IF NOT EXISTS candidates (
    candidate_id INTEGER PRIMARY KEY,
    experience_years REAL NOT NULL CHECK (experience_years >= 0),
    education_level TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id INTEGER PRIMARY KEY,
    job_title TEXT NOT NULL,
    department TEXT NOT NULL,
    job_level INTEGER NOT NULL CHECK (job_level BETWEEN 1 AND 5),
    opened_at TEXT NOT NULL,
    closed_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('Open', 'Filled', 'Cancelled'))
);

CREATE TABLE IF NOT EXISTS applications (
    application_id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    applied_at TEXT NOT NULL,
    source TEXT NOT NULL
        CHECK (source IN ('LinkedIn', 'Referral', 'Career Site', 'Agency', 'Other')),
    status TEXT NOT NULL
        CHECK (status IN ('Active', 'Rejected', 'Withdrawn', 'Hired')),

    FOREIGN KEY (candidate_id)
        REFERENCES candidates(candidate_id),

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
);

CREATE TABLE IF NOT EXISTS stage_events (
    event_id INTEGER PRIMARY KEY,
    application_id INTEGER NOT NULL,
    stage TEXT NOT NULL
        CHECK (stage IN ('Applied', 'Screening', 'Interview', 'Offer', 'Hired')),
    entered_at TEXT NOT NULL,

    FOREIGN KEY (application_id)
        REFERENCES applications(application_id)
);