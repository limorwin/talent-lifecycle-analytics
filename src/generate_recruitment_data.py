import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "recruitment.db"

RNG = np.random.default_rng(42)

# Number of synthetic candidates
N_CANDIDATES = 500

# Generate candidate IDs
candidate_ids = np.arange(1, N_CANDIDATES + 1)

# Generate years of professional experience
experience_years = RNG.uniform(0, 20, size=N_CANDIDATES).round(1)

# Generate education levels
education_levels = RNG.choice(
    ["High School", "Bachelors", "Masters", "PhD"],
    size=N_CANDIDATES,
    p=[0.10, 0.50, 0.30, 0.10]
)

# Generate candidate creation dates
created_dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(
    RNG.integers(0, 365, size=N_CANDIDATES),
    unit="D"
)

# Create a pandas DataFrame
candidates_df = pd.DataFrame({
    "candidate_id": candidate_ids,
    "experience_years": experience_years,
    "education_level": education_levels,
    "created_at": created_dates.strftime("%Y-%m-%d")
})

print(candidates_df.head())
print(f"Total candidates generated: {len(candidates_df)}")

# Number of synthetic jobs
N_JOBS = 30

# Define job titles and their departments
job_options = [
    ("Data Analyst", "Analytics"),
    ("Data Scientist", "Analytics"),
    ("Business Analyst", "Analytics"),
    ("Financial Analyst", "Finance"),
    ("FP&A Manager", "Finance"),
    ("Software Engineer", "Engineering"),
    ("Product Manager", "Product"),
    ("HR Specialist", "Human Resources"),
    ("Recruiter", "Human Resources"),
    ("Marketing Analyst", "Marketing")
]

# Randomly select jobs
selected_jobs = RNG.choice(
    len(job_options),
    size=N_JOBS,
    replace=True
)

# Generate job opening dates
opened_dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(
    RNG.integers(0, 300, size=N_JOBS),
    unit="D"
)

# Create jobs DataFrame
jobs_df = pd.DataFrame({
    "job_id": np.arange(1, N_JOBS + 1),
    "job_title": [job_options[i][0] for i in selected_jobs],
    "department": [job_options[i][1] for i in selected_jobs],
    "job_level": RNG.integers(1, 6, size=N_JOBS),
    "opened_at": opened_dates.strftime("%Y-%m-%d"),
    "closed_at": [None] * N_JOBS,
    "status": ["Open"] * N_JOBS
})

print("\nSynthetic jobs:")
print(jobs_df.head())
print(f"Total jobs generated: {len(jobs_df)}")

# Number of synthetic applications
N_APPLICATIONS = 800

# Generate application IDs
application_ids = np.arange(1, N_APPLICATIONS + 1)

# Randomly assign candidates and jobs
application_candidate_ids = RNG.choice(
    candidates_df["candidate_id"],
    size=N_APPLICATIONS,
    replace=True
)

application_job_ids = RNG.choice(
    jobs_df["job_id"],
    size=N_APPLICATIONS,
    replace=True
)

sources = ["LinkedIn", "Referral", "Career Site", "Agency", "Other"]

application_sources = RNG.choice(
    sources,
    size=N_APPLICATIONS,
    p=[0.40, 0.20, 0.25, 0.10, 0.05]
)

applications_preview = pd.DataFrame({
    "application_id": application_ids,
    "candidate_id": application_candidate_ids,
    "job_id": application_job_ids,
    "source": application_sources
})

print("\nSynthetic application assignments:")
print(applications_preview.head())
print(f"Total applications generated: {len(applications_preview)}")

duplicate_count = applications_preview.duplicated(
    subset=["candidate_id", "job_id"]
).sum()

print(f"Duplicate candidate-job pairs: {duplicate_count}")

# Remove duplicate candidate-job combinations
applications_preview = applications_preview.drop_duplicates(
    subset=["candidate_id", "job_id"],
    keep="first"
).copy()

# Reset the application IDs
applications_preview = applications_preview.reset_index(drop=True)

applications_preview["application_id"] = np.arange(
    1, len(applications_preview) + 1
)

print(f"Applications after removing duplicates: {len(applications_preview)}")

# Replenish applications until we reach 800 unique records
while len(applications_preview) < N_APPLICATIONS:

    candidate_id = int(RNG.choice(candidates_df["candidate_id"]))
    job_id = int(RNG.choice(jobs_df["job_id"]))

    # Check whether this candidate already applied to this job
    exists = (
        (applications_preview["candidate_id"] == candidate_id)
        & (applications_preview["job_id"] == job_id)
    ).any()

    if not exists:
        source = RNG.choice(
            sources,
            p=[0.40, 0.20, 0.25, 0.10, 0.05]
        )

        applications_preview.loc[len(applications_preview)] = {
            "application_id": len(applications_preview) + 1,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "source": source
        }

print(f"Final application count: {len(applications_preview)}")

print(
    "Remaining duplicates:",
    applications_preview.duplicated(
        subset=["candidate_id", "job_id"]
    ).sum()
)

# Look up candidate creation dates and job opening dates
candidate_dates = candidates_df.set_index("candidate_id")["created_at"]
job_dates = jobs_df.set_index("job_id")["opened_at"]

# Match dates to each application
applications_preview["candidate_created_at"] = pd.to_datetime(
    applications_preview["candidate_id"].map(candidate_dates)
)

applications_preview["job_opened_at"] = pd.to_datetime(
    applications_preview["job_id"].map(job_dates)
)

# Earliest possible application date
earliest_dates = applications_preview[
    ["candidate_created_at", "job_opened_at"]
].max(axis=1)

# Add a random delay of 0–30 days
application_delays = pd.to_timedelta(
    RNG.integers(0, 31, size=N_APPLICATIONS),
    unit="D"
)

applications_preview["applied_at"] = (
    earliest_dates + application_delays
).dt.strftime("%Y-%m-%d")

invalid_dates = (
    (pd.to_datetime(applications_preview["applied_at"])
     < applications_preview["candidate_created_at"])
    |
    (pd.to_datetime(applications_preview["applied_at"])
     < applications_preview["job_opened_at"])
).sum()

print(f"Applications with invalid dates: {invalid_dates}")

print(
    applications_preview[
        ["application_id", "candidate_id", "job_id", "applied_at"]
    ].head()
)

# Generate initial statuses without hires
application_statuses = RNG.choice(
    ["Active", "Rejected", "Withdrawn"],
    size=N_APPLICATIONS,
    p=[0.20, 0.68, 0.12]
)

applications_preview["status"] = application_statuses

# Create the final applications DataFrame
applications_df = applications_preview[
    [
        "application_id",
        "candidate_id",
        "job_id",
        "applied_at",
        "source",
        "status"
    ]
].copy()

# Select 20 jobs to be filled
filled_job_ids = RNG.choice(
    jobs_df["job_id"],
    size=20,
    replace=False
)

# Assign exactly one hire to each filled job
for job_id in filled_job_ids:

    eligible = applications_df[
        applications_df["job_id"] == job_id
    ]

    hired_application_id = int(
        RNG.choice(eligible["application_id"])
    )

    applications_df.loc[
        applications_df["application_id"] == hired_application_id,
        "status"
    ] = "Hired"

# Update job statuses
jobs_df.loc[
    jobs_df["job_id"].isin(filled_job_ids),
    "status"
] = "Filled"


print("\nFinal applications:")
print(applications_df.head())

print("\nFinal application statuses:")
print(applications_df["status"].value_counts())

print("\nJob statuses:")
print(jobs_df["status"].value_counts())

hires_per_job = (
    applications_df[applications_df["status"] == "Hired"]
    .groupby("job_id")
    .size()
)

print("\nMaximum hires per job:", hires_per_job.max())

# Possible recruitment paths by application status
stage_paths = {
    "Hired": ["Applied", "Screening", "Interview", "Offer", "Hired"],
    "Rejected": [
        ["Applied"],
        ["Applied", "Screening"],
        ["Applied", "Screening", "Interview"],
        ["Applied", "Screening", "Interview", "Offer"]
    ],
    "Withdrawn": [
        ["Applied"],
        ["Applied", "Screening"],
        ["Applied", "Screening", "Interview"]
    ],
    "Active": [
        ["Applied"],
        ["Applied", "Screening"],
        ["Applied", "Screening", "Interview"],
        ["Applied", "Screening", "Interview", "Offer"]
    ]
}

stage_records = []

for _, application in applications_df.iterrows():

    status = application["status"]

    if status == "Hired":
        stages = stage_paths["Hired"]
    else:
        possible_paths = stage_paths[status]
        stages = possible_paths[
            RNG.integers(0, len(possible_paths))
        ]

    stage_records.append({
        "application_id": application["application_id"],
        "stages": stages
    })

stage_paths_df = pd.DataFrame(stage_records)

print("\nSample recruitment paths:")
print(stage_paths_df.head(10))

# Typical simulated delays between recruitment stages
stage_delays = {
    "Screening": (1, 5),
    "Interview": (3, 10),
    "Offer": (5, 14),
    "Hired": (2, 7)
}

latest_application_dates = (
    applications_df.groupby("job_id")["applied_at"]
    .max()
)

print("\nLatest application dates:")
print(latest_application_dates.head())

stage_events = []

for _, application in applications_df.iterrows():

    application_id = application["application_id"]
    applied_at = pd.Timestamp(application["applied_at"])

    stages = stage_paths_df.loc[
        stage_paths_df["application_id"] == application_id,
        "stages"
    ].iloc[0]

    current_date = applied_at

    for stage in stages:

        if stage != "Applied":
            min_days, max_days = stage_delays[stage]

            delay = int(RNG.integers(min_days, max_days + 1))
            current_date += pd.Timedelta(days=delay)

        stage_events.append({
            "application_id": application_id,
            "stage": stage,
            "entered_at": current_date.strftime("%Y-%m-%d")
        })

stage_events_df = pd.DataFrame(stage_events)

# Assign unique event IDs
stage_events_df.insert(
    0,
    "event_id",
    np.arange(1, len(stage_events_df) + 1)
)

# NEW: Adjust hiring dates
latest_application_dates = (
    applications_df.groupby("job_id")["applied_at"].max()
)

hired_applications = applications_df.loc[
    applications_df["status"] == "Hired",
    ["application_id", "job_id"]
]

for _, hired_app in hired_applications.iterrows():

    application_id = hired_app["application_id"]
    job_id = hired_app["job_id"]

    latest_applied = pd.Timestamp(
        latest_application_dates.loc[job_id]
    )

    hire_mask = (
        (stage_events_df["application_id"] == application_id)
        & (stage_events_df["stage"] == "Hired")
    )

    current_hire_date = pd.Timestamp(
        stage_events_df.loc[hire_mask, "entered_at"].iloc[0]
    )

    new_hire_date = max(
        current_hire_date,
        latest_applied + pd.Timedelta(days=1)
    )

    stage_events_df.loc[hire_mask, "entered_at"] = (
        new_hire_date.strftime("%Y-%m-%d")
    )

print("\nGenerated stage events:")
print(stage_events_df.head(15))
print(f"Total stage events: {len(stage_events_df)}")

# Every application should have exactly one Applied event
applied_count = (
    stage_events_df["stage"] == "Applied"
).sum()

# Every hired application should have a Hired event
hired_event_count = (
    stage_events_df["stage"] == "Hired"
).sum()

# Check that stage dates never precede application dates
events_with_applications = stage_events_df.merge(
    applications_df[["application_id", "applied_at"]],
    on="application_id"
)

invalid_event_dates = (
    pd.to_datetime(events_with_applications["entered_at"])
    < pd.to_datetime(events_with_applications["applied_at"])
).sum()

print(f"Applied events: {applied_count}")
print(f"Hired events: {hired_event_count}")
print(f"Invalid stage dates: {invalid_event_dates}")

# Find the date each successful candidate was hired
hired_events = stage_events_df[
    stage_events_df["stage"] == "Hired"
]

# Connect hired events to their jobs
hired_jobs = hired_events.merge(
    applications_df[["application_id", "job_id"]],
    on="application_id"
)

# Create a lookup: job_id -> hire date
job_closing_dates = hired_jobs.set_index("job_id")["entered_at"]

# Update closing dates for filled jobs
jobs_df["closed_at"] = jobs_df["job_id"].map(job_closing_dates)

print("\nJob closing dates:")
print(jobs_df[["job_id", "status", "opened_at", "closed_at"]].head(10))

filled_without_close = (
    (jobs_df["status"] == "Filled")
    & jobs_df["closed_at"].isna()
).sum()

open_with_close = (
    (jobs_df["status"] == "Open")
    & jobs_df["closed_at"].notna()
).sum()

invalid_closing_dates = (
    pd.to_datetime(jobs_df["closed_at"])
    < pd.to_datetime(jobs_df["opened_at"])
).sum()

print(f"Filled jobs without closing dates: {filled_without_close}")
print(f"Open jobs with closing dates: {open_with_close}")
print(f"Closing dates before opening dates: {invalid_closing_dates}")

# Add job information to each application
applications_check = applications_df.merge(
    jobs_df[["job_id", "status", "closed_at"]],
    on="job_id",
    suffixes=("_application", "_job")
)

# Find applications submitted after the job closed
late_applications = (
    pd.to_datetime(applications_check["applied_at"])
    > pd.to_datetime(applications_check["closed_at"])
)

# Find active applications for filled jobs
active_on_filled_jobs = (
    (applications_check["status_application"] == "Active")
    & (applications_check["status_job"] == "Filled")
)

print(f"Applications after job closing: {late_applications.sum()}")
print(f"Active applications on filled jobs: {active_on_filled_jobs.sum()}")

# Identify filled jobs
filled_jobs = jobs_df.loc[
    jobs_df["status"] == "Filled",
    "job_id"
]

# Find active applications belonging to filled jobs
mask = (
    applications_df["job_id"].isin(filled_jobs)
    & (applications_df["status"] == "Active")
)

print(f"Active applications to resolve: {mask.sum()}")

# Mark these applications as rejected
applications_df.loc[mask, "status"] = "Rejected"

print(
    "Remaining active applications on filled jobs:",
    (
        applications_df["job_id"].isin(filled_jobs)
        & (applications_df["status"] == "Active")
    ).sum()
)

# Refresh the joined data after our status updates
applications_check = applications_df.merge(
    jobs_df[["job_id", "status", "opened_at", "closed_at"]],
    on="job_id",
    suffixes=("_application", "_job")
)

# Identify applications submitted after their jobs closed
late_mask = (
    pd.to_datetime(applications_check["applied_at"])
    > pd.to_datetime(applications_check["closed_at"])
)

late_examples = applications_check.loc[
    late_mask,
    [
        "application_id",
        "candidate_id",
        "job_id",
        "applied_at",
        "opened_at",
        "closed_at",
        "status_application"
    ]
]

print("\nExamples of late applications:")
print(late_examples.head(10))

# Connect stage events to applications and jobs
events_check = (
    stage_events_df
    .merge(
        applications_df[["application_id", "job_id"]],
        on="application_id"
    )
    .merge(
        jobs_df[["job_id", "closed_at"]],
        on="job_id"
    )
)

# Check events occurring after job closure
events_after_closing = (
    pd.to_datetime(events_check["entered_at"])
    > pd.to_datetime(events_check["closed_at"])
)

print(
    "Stage events after job closing:",
    events_after_closing.sum()
)

# Check chronological order within each application
ordered_events = stage_events_df.sort_values(
    ["application_id", "event_id"]
).copy()

ordered_events["previous_date"] = (
    ordered_events.groupby("application_id")["entered_at"]
    .shift(1)
)

invalid_stage_order = (
    pd.to_datetime(ordered_events["entered_at"])
    < pd.to_datetime(ordered_events["previous_date"])
).sum()

print(
    "Stage events out of chronological order:",
    invalid_stage_order
)

# Identify stage events occurring after job closure
late_event_ids = events_check.loc[
    events_after_closing,
    "event_id"
]

print("\nLate stage events by stage:")
print(
    events_check.loc[events_after_closing, "stage"]
    .value_counts()
)

# Remove events that occur after job closing
stage_events_df = stage_events_df.loc[
    ~stage_events_df["event_id"].isin(late_event_ids)
].copy()

# Reset event IDs
stage_events_df = stage_events_df.reset_index(drop=True)

stage_events_df["event_id"] = np.arange(
    1, len(stage_events_df) + 1
)

print(f"\nStage events after cleanup: {len(stage_events_df)}")

# Recheck stage events against job closing dates
final_events_check = (
    stage_events_df
    .merge(
        applications_df[["application_id", "job_id"]],
        on="application_id"
    )
    .merge(
        jobs_df[["job_id", "closed_at"]],
        on="job_id"
    )
)

remaining_late_events = (
    pd.to_datetime(final_events_check["entered_at"])
    > pd.to_datetime(final_events_check["closed_at"])
).sum()

print(f"Remaining late stage events: {remaining_late_events}")

print(
    "Final stage event count:",
    len(stage_events_df)
)

# Count Applied events per application
applied_counts = (
    stage_events_df[stage_events_df["stage"] == "Applied"]
    .groupby("application_id")
    .size()
)

# Count Hired events per application
hired_counts = (
    stage_events_df[stage_events_df["stage"] == "Hired"]
    .groupby("application_id")
    .size()
)

# Check every application has exactly one Applied event
invalid_applied = (
    applications_df["application_id"]
    .map(applied_counts)
    .fillna(0)
    .ne(1)
    .sum()
)

# Compare Hired events with application statuses
applications_with_hire_events = applications_df[
    applications_df["application_id"].isin(hired_counts.index)
]

invalid_hired_status = (
    applications_with_hire_events["status"] != "Hired"
).sum()

hired_without_event = (
    (applications_df["status"] == "Hired")
    & ~applications_df["application_id"].isin(hired_counts.index)
).sum()

print(f"Applications without exactly one Applied event: {invalid_applied}")
print(f"Hired events: {hired_counts.sum()}")
print(f"Hired events with incorrect status: {invalid_hired_status}")
print(f"Hired applications without Hired event: {hired_without_event}")

# Create a separate database for synthetic data
SYNTHETIC_DB_PATH = (
    PROJECT_ROOT / "data" / "processed" / "recruitment_synthetic.db"
)

SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"

# Read the existing database schema
schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

# Prevent accidental overwriting of an existing database
if SYNTHETIC_DB_PATH.exists():
    raise FileExistsError(
        f"Database already exists: {SYNTHETIC_DB_PATH}"
    )

# Connect to SQLite
conn = sqlite3.connect(SYNTHETIC_DB_PATH)

try:
    conn.execute("PRAGMA foreign_keys = ON")

    # Create the four tables
    conn.executescript(schema_sql)

    # Insert data in foreign-key dependency order
    candidates_df.to_sql(
        "candidates", conn, if_exists="append", index=False
    )

    jobs_df.to_sql(
        "jobs", conn, if_exists="append", index=False
    )

    applications_df.to_sql(
        "applications", conn, if_exists="append", index=False
    )

    stage_events_df.to_sql(
        "stage_events", conn, if_exists="append", index=False
    )

    print("\nSynthetic database created successfully!")

    for table_name in [
    "candidates", "jobs", "applications", "stage_events"
    ]:
        count = conn.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

        print(f"{table_name}: {count}")

    foreign_key_errors = conn.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    print("Foreign key errors:", len(foreign_key_errors))

finally:
    conn.close()