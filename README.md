# Talent Acquisition & Employee Lifecycle Analytics
**[Launch the Live Dashboard](https://talent-lifecycle-analytics.streamlit.app/)**

An end-to-end recruitment analytics portfolio project combining **Python, SQL, Streamlit, and Generative AI** to analyze hiring performance and support data-driven recruitment decisions.

## Project Overview

This project demonstrates how recruitment data can be transformed into actionable insights through an interactive analytics dashboard and an AI-powered assistant.

The application uses a synthetic recruitment dataset and supports analysis of application volumes, recruitment funnels, hiring rates, and time-to-hire metrics.

## Key Features

### Interactive Recruitment Dashboard

- Recruitment KPIs, including application counts, total hires, and time to hire
- Application volume by department and recruitment source
- Recruitment funnel and stage conversion analysis
- Recruitment source effectiveness and hiring rates
- Interactive filters for departments, sources, recruitment stages, and application dates
- Excel report export

### AI-Powered Analytics Assistant

An LLM-powered assistant allows users to ask recruitment questions in natural language.

The assistant:

1. Interprets the user's question using OpenAI.
2. Generates a SQLite query based on the database schema and recruitment business definitions.
3. Executes the query against a read-only database connection.
4. Returns a concise natural-language answer and relevant data.
5. Makes the generated SQL available for inspection.

SQL execution includes table-access restrictions, a five-second execution timeout, and a maximum of 100 returned rows.

The assistant currently supports up to 10 questions between conversation resets. This is a user-interface limit, not a guaranteed API spending cap.

## Technology Stack

- **Python 3.12** — Data processing and application logic
- **SQLite** — Recruitment data storage
- **SQL** — Recruitment analytics and metrics
- **Pandas** — Data manipulation
- **Streamlit** — Interactive dashboard and chat interface
- **Altair** — Data visualization
- **OpenAI API** — Natural-language-to-SQL generation and result explanations
- **OpenPyXL** — Excel report export

## Database

The synthetic recruitment database contains four tables:

| Table | Description |
|---|---|
| `candidates` | Candidate profiles |
| `jobs` | Job openings and departments |
| `applications` | Applications and recruitment sources |
| `stage_events` | Recruitment pipeline stage history |

The dataset includes approximately 500 candidates, 30 jobs, 800 applications, and 2,005 stage events.

All recruitment records are synthetic and do not represent real employees or candidates.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/limorwin/talent-lifecycle-analytics.git
cd talent-lifecycle-analytics
```

### 2. Create the Conda environment

```bash
conda env create -f environment.yml
conda activate talent-analytics
```

### 3. Generate the synthetic database

```bash
python src/generate_recruitment_data.py
```

### 4. Configure the OpenAI API key

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key_here
```

The `.env` file is excluded from Git.

OpenAI API usage may incur charges.

### 5. Launch the application

```bash
streamlit run src/app.py
```

## Example Questions

The AI assistant can answer questions such as:

- How many applications came from LinkedIn?
- Which department received the most applications?
- Which recruitment source has the highest hiring rate?
- What is the average time to hire?
- How many candidates reached the interview stage?

## Limitations and Future Improvements

- The dataset is synthetic; results are illustrative rather than real-world recruitment benchmarks.
- AI-generated SQL may be syntactically valid but analytically incorrect. Important findings should be verified against the underlying data and metric definitions.
- The AI assistant queries the full database independently of the dashboard's sidebar filters.
- API usage incurs costs and requires appropriate billing controls.
- The current application is designed as a portfolio MVP, not a production-grade multi-user system.

## Project Purpose

This project demonstrates practical skills in data analytics, relational databases, interactive dashboard development, recruitment metrics, and integrating large language models into analytics workflows.

