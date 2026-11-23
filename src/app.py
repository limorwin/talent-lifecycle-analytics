import sqlite3
from pathlib import Path
from datetime import timedelta
from io import BytesIO

import pandas as pd
import streamlit as st
import altair as alt

from ai_assistant import generate_sql, execute_read_only_query, explain_results

st.set_page_config(
    page_title="Talent Acquisition Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DB_PATH = PROJECT_ROOT / "data" / "processed" / "recruitment_synthetic.db"

FUNNEL_SQL_PATH = (
    PROJECT_ROOT / "sql" / "analytics" / "recruitment_funnel.sql"
)

TIME_TO_HIRE_SQL_PATH = (
    PROJECT_ROOT / "sql" / "analytics" / "time_to_hire.sql"
)

SOURCE_SQL_PATH = (
    PROJECT_ROOT / "sql" / "analytics" / "source_effectiveness.sql"
)

SQL_PATH = (
    PROJECT_ROOT
    / "sql"
    / "analytics"
    / "applications_by_department_source.sql"
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
.kpi-card {
    text-align: center;
    height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.kpi-label {
    font-size: 15px;
    font-weight: 600;
    color: #475569;
    text-align: center;
    white-space: normal;
    overflow-wrap: break-word;
    min-height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.kpi-value {
    font-size: 29px;
    font-weight: 600;
    color: #1F2937;
    margin-top: 10px;
    line-height: 1.2;
}

.kpi-unit {
    font-size: 12px;
    color: #64748B;
    margin-top: 4px;
}
    </style>
    """,
    unsafe_allow_html=True
)

query = SQL_PATH.read_text(encoding="utf-8")
funnel_query = FUNNEL_SQL_PATH.read_text(encoding="utf-8")
time_to_hire_query = TIME_TO_HIRE_SQL_PATH.read_text(
    encoding="utf-8"
)
source_query = SOURCE_SQL_PATH.read_text(encoding="utf-8")

# Load department names for the sidebar
with sqlite3.connect(DB_PATH) as conn:
    departments_df = pd.read_sql_query(
        "SELECT DISTINCT department FROM jobs ORDER BY department",
        conn
    )

# Department filter
st.sidebar.header("Filters")

selected_departments = st.sidebar.multiselect(
    "Departments",
    options=departments_df["department"].tolist(),
    default=[],
    placeholder="All Departments"
)

if not selected_departments:
    selected_departments = departments_df["department"].tolist()

source_options = [
    "LinkedIn",
    "Referral",
    "Career Site",
    "Agency",
    "Other"
]

selected_sources = st.sidebar.multiselect(
    "Recruitment Sources",
    options=source_options,
    default=[],
    placeholder="All Sources"
)

if not selected_sources:
    selected_sources = source_options

stage_options = [
    "Applied",
    "Screening",
    "Interview",
    "Offer",
    "Hired"
]

selected_stages = st.sidebar.multiselect(
    "Recruitment Stages Reached",
    options=stage_options,
    default=[],
    placeholder="All Stages"
)

# Date range filter
with sqlite3.connect(DB_PATH) as conn:
    date_bounds = pd.read_sql_query(
        """
        SELECT
            MIN(applied_at) AS min_date,
            MAX(applied_at) AS max_date
        FROM applications
        """,
        conn
    )

min_date = pd.to_datetime(date_bounds.loc[0, "min_date"]).date()
max_date = pd.to_datetime(date_bounds.loc[0, "max_date"]).date()

date_option = st.sidebar.selectbox(
    "Application Date Range",
    options=[
        "All Dates",
        "Last 30 Days",
        "Last 90 Days",
        "Last 12 Months",
        "Custom Range"
    ]
)

if date_option == "All Dates":
    start_date, end_date = min_date, max_date

elif date_option == "Last 30 Days":
    end_date = max_date
    start_date = max(min_date, end_date - timedelta(days=29))

elif date_option == "Last 90 Days":
    end_date = max_date
    start_date = max(min_date, end_date - timedelta(days=89))

elif date_option == "Last 12 Months":
    end_date = max_date
    start_date = max(min_date, end_date - timedelta(days=364))

else:
    start_date = st.sidebar.date_input(
        "Start Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )

    end_date = st.sidebar.date_input(
        "End Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )

    if start_date > end_date:
        st.sidebar.error("Start date must be before end date.")
        st.stop()

stage_filter_active = bool(selected_stages)

stage_placeholders = (
    ",".join("?" for _ in selected_stages)
    if stage_filter_active
    else "NULL"
)

all_stages = "0" if stage_filter_active else "1"

# Create one SQL placeholder per selected department
department_placeholders = ",".join("?" for _ in selected_departments)
source_placeholders = ",".join("?" for _ in selected_sources)

# Insert placeholders into each SQL query
filtered_query = (
    query
    .replace("{department_placeholders}", department_placeholders)
    .replace("{source_placeholders}", source_placeholders)
    .replace("{stage_placeholders}", stage_placeholders)
    .replace("{all_stages}", all_stages)
)

filtered_funnel_query = (
    funnel_query
    .replace("{department_placeholders}", department_placeholders)
    .replace("{source_placeholders}", source_placeholders)
)

filtered_hiring_query = (
    time_to_hire_query
    .replace("{department_placeholders}", department_placeholders)
    .replace("{source_placeholders}", source_placeholders)
)

filtered_source_query = (
    source_query
    .replace("{department_placeholders}", department_placeholders)
    .replace("{source_placeholders}", source_placeholders)
)

date_params = [start_date.isoformat(), end_date.isoformat()]

base_params = selected_departments + selected_sources + date_params

# Load filtered data
with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query(
        filtered_query,
        conn,
        params = (base_params + selected_stages
        )
    )

    funnel_df = pd.read_sql_query(
        filtered_funnel_query,
        conn,
        params=base_params
    )

    hiring_df = pd.read_sql_query(
        filtered_hiring_query, conn, params=base_params
    )

    source_df = pd.read_sql_query(
        filtered_source_query, conn, params=base_params
    )


avg_time_to_hire = hiring_df["time_to_hire_days"].mean()
median_time_to_hire = hiring_df["time_to_hire_days"].median()
total_hires = len(hiring_df)

print(f"Average time-to-hire: {avg_time_to_hire:.1f} days")
print(f"Median time-to-hire: {median_time_to_hire:.1f} days")
print(f"Total hires: {total_hires}")

st.caption("PEOPLE ANALYTICS  /  RECRUITMENT")

st.title("Talent Acquisition Overview")

st.markdown(
    "Monitor application volume, recruitment channels, "
    "and hiring performance."
)

st.divider()

total_applications = df["application_count"].sum()

total_applications = df["application_count"].sum()

applications_label = (
    "Applications"
    if not selected_stages
    else "Reached: " + ", ".join(selected_stages)
)

# First row
col1, col2, col3 = st.columns(3)

# KPI values
kpis = [
    (applications_label, f"{total_applications:,}", ""),
    ("Departments", str(df["department"].nunique()), ""),
    ("Total Hires", str(total_hires), ""),
    ("Avg. Hire Time", f"{avg_time_to_hire:.0f}", "days"),
    ("Median Hire Time", f"{median_time_to_hire:.0f}", "days"),
]

# Display five matching KPI cards
cols = st.columns(5, gap="small")

for col, (label, value, unit) in zip(cols, kpis):
    with col:
        with st.container(border=True , height=140):
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-unit">{unit or '&nbsp;'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

st.caption(
    "Time-to-hire metrics are based on synthetic recruitment data. "
    "Hiring dates were adjusted during generation and should not "
    "be interpreted as real-world benchmarks."
)

st.subheader("Applications by Department and Source")

source_colors = [
    "#2563EB",  # LinkedIn
    "#60A5FA",  # Referral
    "#0F766E",  # Career Site
    "#7C3AED",  # Agency
    "#F59E0B"   # Other
]

stacked_chart = (
    alt.Chart(df)
    .mark_bar(cornerRadiusEnd=4)
    .encode(
        y=alt.Y(
            "department:N",
            sort="-x",
            title=None,
            scale=alt.Scale(
                paddingInner=0.3,
                paddingOuter=0.2
            ),
            axis=alt.Axis(
                labelFontSize=15,
                labelLimit=200
            )
        ),
        x=alt.X(
            "sum(application_count):Q",
            title="Applications",
            stack="zero",
            axis=alt.Axis(
                labelFontSize=14,
                titleFontSize=15,
                tickMinStep=1
            )
        ),
        color=alt.Color(
            "source:N",
            scale=alt.Scale(
                domain=[
                    "LinkedIn", "Referral", "Career Site",
                    "Agency", "Other"
                ],
                range=[
                    "#2563EB", "#60A5FA", "#0F766E",
                    "#7C3AED", "#F59E0B"
                ]
            ),
            legend=alt.Legend(
                title="Recruitment Source",
                orient="bottom",
                labelFontSize=13
            )
        ),
        tooltip=[
            alt.Tooltip("department:N", title="Department"),
            alt.Tooltip("source:N", title="Source"),
            alt.Tooltip(
                "application_count:Q",
                title="Applications"
            )
        ]
    )
    .properties(height=alt.Step(45))
)

st.altair_chart(stacked_chart, width="stretch")

display_df = df.rename(
    columns={
        "department": "Department",
        "source": "Recruitment Source",
        "application_count": "Applications"
    }
)

st.caption(
    f"Total: {display_df['Applications'].sum():,} applications"
)

with st.expander("View application details"):
    st.dataframe(
        display_df,
        hide_index=True,
        width="stretch",
        height="content",
        column_config={
            "Department": st.column_config.TextColumn(
                "Department",
                width="medium"
            ),
            "Recruitment Source": st.column_config.TextColumn(
                "Recruitment Source",
                width="medium"
            ),
            "Applications": st.column_config.NumberColumn(
                "Applications",
                format="%d"
            )
        }
    )

left_col, right_col = st.columns(2, gap="medium")

with left_col:
    st.subheader("Recruitment Funnel")

    funnel_chart = (
        alt.Chart(funnel_df)
        .mark_bar(
            cornerRadiusEnd=5,
            size=24
        )
        .encode(
            y=alt.Y(
                "stage:N",
                sort=[
                    "Applied",
                    "Screening",
                    "Interview",
                    "Offer",
                    "Hired"
                ],
                title=None,
                axis=alt.Axis(
                    labelFontSize=15,
                    labelLimit=200
                )
            ),
            x=alt.X(
                "application_count:Q",
                title="Applications",
                axis=alt.Axis(
                    labelFontSize=14,
                    titleFontSize=15,
                    tickMinStep=1
                )
            ),
            color=alt.condition(
                alt.FieldOneOfPredicate(
                    field="stage",
                    oneOf=selected_stages
                ),
                alt.value("#F59E0B"),
                alt.value("#2563EB")
            ),
            tooltip=[
                alt.Tooltip("stage:N", title="Stage"),
                alt.Tooltip(
                    "application_count:Q",
                    title="Applications"
                ),
                alt.Tooltip(
                    "conversion_rate:Q",
                    title="Conversion (%)",
                    format=".1f"
                )
            ]
        )
        .properties(height=250)
    )

    st.altair_chart(funnel_chart, width="stretch")

    funnel_display = funnel_df.rename(
        columns={
            "stage": "Stage",
            "application_count": "Applications",
            "conversion_rate": "Conversion Rate (%)"
        }
    )

    funnel_display["Conversion Rate (%)"] = (
        funnel_display["Conversion Rate (%)"]
        .apply(lambda x: f"{float(x):.1f}%" if pd.notna(x) else "—")
    )

    def highlight_stage(row):
        if row["Stage"] in selected_stages:
            return ["background-color: #FFF3CD"] * len(row)
        return [""] * len(row)
    with st.expander("View funnel details"):
        st.dataframe(
            funnel_display,
            hide_index=True,
            use_container_width=True
        )

with right_col:
    st.subheader("Recruitment Source Effectiveness")

    source_chart = (
        alt.Chart(source_df)
        .mark_bar(
            color="#2563EB",
            cornerRadiusEnd=5,
            size=24
        )
        .encode(
            y=alt.Y(
                "source:N",
                sort="-x",
                title=None,
                axis=alt.Axis(
                    labelFontSize=15,
                    labelLimit=200
                )
            ),
            x=alt.X(
                "hire_rate:Q",
                title="Hire Rate (%)",
                axis=alt.Axis(
                    labelFontSize=14,
                    titleFontSize=15,
                    format=".1f"
                )
            ),
            tooltip=[
                alt.Tooltip("source:N", title="Source"),
                alt.Tooltip("total_applications:Q", title="Applications"),
                alt.Tooltip("total_hires:Q", title="Hires"),
                alt.Tooltip("hire_rate:Q", title="Hire Rate (%)", format=".1f")
            ]
        )
        .properties(height=250)
    )

    st.altair_chart(source_chart, width="stretch")

    source_display = source_df.rename(
        columns={
            "source": "Source",
            "total_applications": "Applications",
            "total_hires": "Hires",
            "hire_rate": "Hire Rate (%)"
        }
    )

    source_display["Hire Rate (%)"] = (
        source_display["Hire Rate (%)"]
        .apply(lambda x: f"{float(x):.1f}%" if pd.notna(x) else "—")
    )

    with st.expander("View source details"):
        st.dataframe(
            source_display,
            hide_index=True,
            use_container_width=True,
            width="stretch",
            height="content"
        )

def create_excel_export():
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        display_df.to_excel(
            writer,
            sheet_name="Applications",
            index=False
        )

        funnel_display.to_excel(
            writer,
            sheet_name="Recruitment Funnel",
            index=False
        )

        source_display.to_excel(
            writer,
            sheet_name="Source Effectiveness",
            index=False
        )

    return output.getvalue()

st.download_button(
    label="Download Excel Report",
    data=create_excel_export(),
    file_name="talent_acquisition_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    icon=":material/download:"
)



# AI Analytics Assistant
st.divider()
st.header("AI Recruitment Analytics Assistant")

MAX_QUESTIONS = 10

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("Clear conversation", icon=":material/delete_outline:"):
    st.session_state.chat_history = []
    st.session_state.ai_questions_used = 0
    st.rerun()

if "ai_questions_used" not in st.session_state:
    st.session_state.ai_questions_used = 0

st.caption(
    f"Ask questions about recruitment data. "
    f"{st.session_state.ai_questions_used}/{MAX_QUESTIONS} "
    "AI questions used this session."
)

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("data") is not None:
            st.dataframe(message["data"], hide_index=True, use_container_width=True)

        if "sql" in message:
            with st.expander("View SQL"):
                st.code(message["sql"], language="sql")

question = st.chat_input(
    "Ask a recruitment analytics question...",
    disabled=st.session_state.ai_questions_used >= MAX_QUESTIONS
)

if question:
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    st.session_state.ai_questions_used += 1

    with st.chat_message("assistant"):
        try:
            with st.spinner("Analyzing recruitment data..."):
                sql = generate_sql(question)
                result = execute_read_only_query(sql)
                answer = explain_results(question, result)

            # Display a natural-language summary for single-number results
            st.markdown(answer)

            if result.shape[0] > 1:
                st.dataframe(result, hide_index=True, use_container_width=True)

            with st.expander("View SQL"):
                st.code(sql, language="sql")

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer,
                "sql": sql,
                "data": result if result.shape[0] > 1 else None
            })

        except Exception:
            st.error(
                "Unable to answer this question. "
                "Check your API configuration or try again."
            )
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "Unable to answer this question."
            })
