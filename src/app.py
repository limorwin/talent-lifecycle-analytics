import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

import altair as alt

st.set_page_config(
    page_title="Talent Acquisition Analytics",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        text-align: center;
    }

    [data-testid="stMetricLabel"] {
        justify-content: center;
        width: 100%;
    }

    [data-testid="stMetricValue"] {
        justify-content: center;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DB_PATH = PROJECT_ROOT / "data" / "processed" / "recruitment.db"

SQL_PATH = (
    PROJECT_ROOT
    / "sql"
    / "analytics"
    / "applications_by_department_source.sql"
)

query = SQL_PATH.read_text(encoding="utf-8")

with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query(query, conn)

st.caption("PEOPLE ANALYTICS  /  RECRUITMENT")

st.title("Talent Acquisition Overview")

st.markdown(
    "Monitor application volume, recruitment channels, "
    "and hiring performance."
)

st.divider()

total_applications = df["application_count"].sum()

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="Total Applications",
        value=int(total_applications),
        border=True
    )

with col2:
    st.metric(
        label="Departments",
        value=df["department"].nunique(),
        border=True
    )

st.subheader("Applications by Department and Source")

display_df = df.rename(
    columns={
        "department": "Department",
        "source": "Recruitment Source",
        "application_count": "Applications"
    }
)

styled_df = (
    display_df.style
    .format({"Applications": "{:.0f}"})
    .set_table_styles([
        {
            "selector": "th.col_heading",
            "props": [
                ("background-color", "#E8EEF7"),
                ("color", "#17365D"),
                ("font-weight", "bold"),
                ("text-align", "center"),
                ("font-size", "16px")
            ]
        },
        {
            "selector": "td.col2",
            "props": [
                ("text-align", "center")
            ]
        }
    ])
    .hide(axis="index")
)

st.table(styled_df)

st.subheader("Applications by Department")

department_df = (
    df.groupby("department")["application_count"]
    .sum()
    .reset_index()
)

chart = (
    alt.Chart(department_df)
    .mark_bar(
        color="#2563EB",
        cornerRadiusEnd=5,
        size=30
    )
    .encode(
        y=alt.Y(
            "department:N",
            sort="-x",
            title=None,
            axis=alt.Axis(
                labelFontSize=15
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
        tooltip=[
            alt.Tooltip("department:N", title="Department"),
            alt.Tooltip("application_count:Q", title="Applications")
        ]
    )
    .properties(height=180)
)

st.altair_chart(chart, use_container_width=True)