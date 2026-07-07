"""
Faculty Eligibility & Student-Faculty Ratio Dashboard
======================================================
Run with:  streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_faculty_data, validate_dataframe, clean_dataframe
from utils.eligibility import (
    DEFAULT_MIN_EXPERIENCE,
    enrich_with_batch_eligibility,
    student_faculty_ratio,
    generate_batch_options,
)
from utils.styling import inject_global_css, kpi_card, section_title, PRIMARY, SUCCESS, DANGER

# ----------------------------------------------------------------------
# Page config (must be the first Streamlit call)
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Faculty Eligibility Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_global_css()

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.title("🎓 Faculty Eligibility & Student-Faculty Ratio Dashboard")
st.caption(
    "Upload the faculty dataset, choose an academic batch, and instantly see "
    "who is eligible, department-wise breakdowns, and the student-faculty ratio."
)

# ----------------------------------------------------------------------
# SIDEBAR — Data source
# ----------------------------------------------------------------------
st.sidebar.header("📂 Data Source")
uploaded_file = st.sidebar.file_uploader(
    "Upload Faculty CSV/Excel", type=["csv", "xlsx", "xls"]
)

use_sample = False
if uploaded_file is None:
    use_sample = st.sidebar.checkbox("Use bundled sample dataset (data/Facultyyyy_data.xlsx)", value=True)

if uploaded_file is not None:
    try:
        raw_df = load_faculty_data(uploaded_file)
    except ValueError as e:
        st.error(str(e))
        st.stop()
elif use_sample:
    raw_df = clean_dataframe(pd.read_excel("data/Facultyyyy_data.xlsx"))
else:
    st.info("👈 Upload a faculty file or check 'Use bundled sample dataset' to begin.")
    st.stop()

warnings = validate_dataframe(raw_df)
if warnings:
    with st.sidebar.expander("⚠️ Data quality warnings", expanded=False):
        for w in warnings:
            st.warning(w)

# ----------------------------------------------------------------------
# SIDEBAR — Academic batch & eligibility norms
# ----------------------------------------------------------------------
st.sidebar.header("🎯 Academic Batch")
batch_options = generate_batch_options(raw_df)
default_idx = min(3, len(batch_options) - 1)
selected_batch = st.sidebar.selectbox(
    "Select Academic Batch", batch_options, index=default_idx,
    help="Experience is recalculated as on 1st July of the batch's starting year."
)

st.sidebar.header("📏 Minimum Experience Norms (years)")
st.sidebar.caption("Adjust if your institution's eligibility rule differs.")
min_experience = {}
for designation, default_years in DEFAULT_MIN_EXPERIENCE.items():
    min_experience[designation] = st.sidebar.number_input(
        designation, min_value=0, max_value=40, value=int(default_years), step=1
    )

# ----------------------------------------------------------------------
# Compute batch-specific eligibility
# ----------------------------------------------------------------------
df = enrich_with_batch_eligibility(raw_df, selected_batch, min_experience)

# ----------------------------------------------------------------------
# SIDEBAR — Filters
# ----------------------------------------------------------------------
st.sidebar.header("🔍 Filters")

departments = sorted(df["Department"].dropna().unique())
selected_depts = st.sidebar.multiselect("Department", departments, default=departments)

designations = sorted(df["Designation"].dropna().unique())
selected_designations = st.sidebar.multiselect("Designation", designations, default=designations)

has_qualification = "Qualification" in df.columns
if has_qualification:
    qualifications = sorted(df["Qualification"].dropna().unique())
    selected_qualifications = st.sidebar.multiselect(
        "Qualification",
        qualifications,
        default=qualifications
    )

eligibility_status = st.sidebar.multiselect(
    "Batch Eligibility", ["Eligible", "Not Eligible"], default=["Eligible", "Not Eligible"]
)

search_term = st.sidebar.text_input("Search by Name or Faculty ID", "")

st.sidebar.header("👨‍🎓 Student Strength")
st.sidebar.caption("Not present in the faculty file — enter manually for the ratio calc.")
total_students = st.sidebar.number_input(
    "Total Students (selected batch)", min_value=0, value=500, step=10
)

# ----------------------------------------------------------------------
# Apply filters
# ----------------------------------------------------------------------
filtered = df[
    df["Department"].isin(selected_depts)
    & df["Designation"].isin(selected_designations)
    & df["Batch Eligibility"].isin(eligibility_status)
]

if has_qualification:
    filtered = filtered[filtered["Qualification"].isin(selected_qualifications)]

if search_term:
    term = search_term.lower()
    filtered = filtered[
        filtered["Faculty Name"].str.lower().str.contains(term)
        | filtered["Faculty ID"].str.lower().str.contains(term)
    ]

# ----------------------------------------------------------------------
# KPI ROW
# ----------------------------------------------------------------------
total_faculty = len(filtered)
eligible_count = (filtered["Batch Eligibility"] == "Eligible").sum()
not_eligible_count = total_faculty - eligible_count
eligibility_rate = round((eligible_count / total_faculty * 100), 1) if total_faculty else 0.0
ratio = student_faculty_ratio(total_students, eligible_count)
ratio_display = f"1 : {ratio}" if ratio is not None else "N/A"

section_title(f"Overview — Batch {selected_batch}")
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    kpi_card("Total Faculty", f"{total_faculty}", "in current filter")
with k2:
    kpi_card("Eligible Faculty", f"{eligible_count}", f"{eligibility_rate}% of total", color=SUCCESS)
with k3:
    kpi_card("Not Eligible", f"{not_eligible_count}", "needs review", color=DANGER)
with k4:
    kpi_card("Total Students", f"{total_students}", "entered manually")
with k5:
    kpi_card("Student : Faculty Ratio", ratio_display, "students per eligible faculty", color=PRIMARY)

st.markdown("---")

# ----------------------------------------------------------------------
# CHARTS ROW 1 — Department distribution & Eligibility split
# ----------------------------------------------------------------------
section_title("Faculty Composition")
c1, c2, c3 = st.columns(3)

with c1:
    dept_counts = filtered["Department"].value_counts().reset_index()
    dept_counts.columns = ["Department", "Count"]

    fig = px.treemap(
        dept_counts,
        path=["Department"],
        values="Count",
        color="Count",
        title="Faculty Distribution by Department",
        color_continuous_scale="Blues"
    )
    fig.update_layout(margin=dict(t=50, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    elig_counts = filtered["Batch Eligibility"].value_counts().reset_index()
    elig_counts.columns = ["Status", "Count"]
    fig = px.pie(
        elig_counts, names="Status", values="Count", hole=0.55,
        title="Eligibility Split",
        color="Status",
        color_discrete_map={"Eligible": SUCCESS, "Not Eligible": DANGER},
    )
    fig.update_traces(textinfo="label+percent")
    fig.update_layout(margin=dict(t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

with c3:
    desig_counts = filtered["Designation"].value_counts().reset_index()
    desig_counts.columns = ["Designation", "Count"]

    fig = px.funnel(
        desig_counts,
        x="Count",
        y="Designation",
        title="Designation Distribution"
    )
    fig.update_layout(margin=dict(t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# CHARTS ROW 2 — Experience distribution & Dept-wise ratio
# ----------------------------------------------------------------------
section_title("Experience & Ratio Analysis")
c4, c5 = st.columns(2)

with c4:
    fig = px.box(
        filtered,
        x="Designation",
        y="Computed Experience",
        color="Designation",
        title=f"Experience Distribution (as of {selected_batch})",
        points="all"
    )
    fig.update_layout(margin=dict(t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

with c5:
    dept_eligible = (
        filtered[filtered["Batch Eligibility"] == "Eligible"]
        .groupby("Department")
        .size()
        .reindex(sorted(filtered["Department"].unique()), fill_value=0)
    )
    n_depts = max(len(dept_eligible), 1)
    per_dept_students = total_students / n_depts
    dept_ratio_df = pd.DataFrame({
        "Department": dept_eligible.index,
        "Eligible Faculty": dept_eligible.values,
    })
    dept_ratio_df["Est. Students"] = per_dept_students
    dept_ratio_df["Ratio"] = dept_ratio_df.apply(
        lambda r: student_faculty_ratio(r["Est. Students"], r["Eligible Faculty"]) or 0, axis=1
    )

    fig = px.bar(
        dept_ratio_df,
        y="Department",
        x="Ratio",
        orientation="h",
        text="Ratio",
        title="Est. Student-Faculty Ratio by Department",
        color="Ratio",
        color_continuous_scale="Viridis"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(margin=dict(t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Assumes total students are split evenly across departments shown. "
        "For exact per-department ratios, provide department-wise student counts."
    )

st.markdown("---")

# ----------------------------------------------------------------------
# SEARCHABLE FACULTY TABLE
# ----------------------------------------------------------------------
section_title("Faculty Details")

display_cols = [
    "Faculty ID", "Faculty Name", "Department", "Designation",
    "Date of Joining", "Experience Years", "Computed Experience", "Batch Eligibility",
]
if has_qualification:
    display_cols.insert(4, "Qualification")

table_df = filtered[display_cols].sort_values("Faculty ID").reset_index(drop=True)


def _eligibility_color(v):
    if v == "Eligible":
        return f"color: {SUCCESS}; font-weight:600;"
    if v == "Not Eligible":
        return f"color: {DANGER}; font-weight:600;"
    return ""


styler = table_df.style
# pandas >= 2.1 renamed Styler.applymap -> Styler.map; support both so this
# works whether you're on an old or new pandas version.
if hasattr(styler, "map"):
    styler = styler.map(_eligibility_color, subset=["Batch Eligibility"])
else:
    styler = styler.applymap(_eligibility_color, subset=["Batch Eligibility"])

st.dataframe(styler, use_container_width=True, height=420)

csv_bytes = table_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Filtered Table as CSV",
    data=csv_bytes,
    file_name=f"faculty_eligibility_{selected_batch}.csv",
    mime="text/csv",
)

st.caption(
    "Built with Streamlit, Pandas & Plotly · Eligibility rule: "
    + ", ".join(f"{k} ≥ {v} yrs" for k, v in min_experience.items())
)
