"""
data_loader.py
----------------
Handles reading the faculty dataset from CSV or Excel, validating that
required columns exist, and doing basic type cleanup. Kept separate so
app.py stays focused on UI/layout.
"""

import pandas as pd
import streamlit as st

REQUIRED_COLUMNS = [
    "Faculty ID",
    "Faculty Name",
    "Department",
    "Designation",
    "Date of Joining",
    "Experience Years",
]


@st.cache_data(show_spinner="Loading faculty data...")
def load_faculty_data(uploaded_file) -> pd.DataFrame:
    """
    Reads an uploaded CSV or Excel file into a DataFrame.
    Cached by Streamlit so re-running the app (e.g. changing a filter)
    doesn't re-parse the file every time.
    """
    if uploaded_file is None:
        return None

    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file type. Please upload a .csv or .xlsx file.")

    return clean_dataframe(df)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from headers/values and validate required columns exist."""
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Uploaded file is missing required column(s): {', '.join(missing)}"
        )

    # Trim whitespace in key text columns
    text_cols = ["Faculty ID", "Faculty Name", "Department", "Designation"]
    if "Qualification" in df.columns:
        text_cols.append("Qualification")
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    df["Experience Years"] = pd.to_numeric(df["Experience Years"], errors="coerce")
    return df


def validate_dataframe(df: pd.DataFrame) -> list:
    """Returns a list of human-readable warnings about data quality issues."""
    warnings = []

    if df["Faculty ID"].duplicated().any():
        n = df["Faculty ID"].duplicated().sum()
        warnings.append(f"{n} duplicate Faculty ID(s) found.")

    bad_dates = pd.to_datetime(df["Date of Joining"], errors="coerce").isna().sum()
    if bad_dates:
        warnings.append(f"{bad_dates} row(s) have an unparseable Date of Joining.")

    missing_exp = df["Experience Years"].isna().sum()
    if missing_exp:
        warnings.append(f"{missing_exp} row(s) have missing/invalid Experience Years.")

    return warnings
