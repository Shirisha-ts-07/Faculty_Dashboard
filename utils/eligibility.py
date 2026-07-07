"""
eligibility.py
----------------
Core business logic for:
  1. Calculating faculty experience as of a chosen academic-batch reference date
  2. Determining eligibility based on Designation-wise minimum experience norms
  3. Computing Student-Faculty Ratio

Kept separate from app.py so the "rules" can be unit-tested / reused
independently of the Streamlit UI.
"""

import pandas as pd
from datetime import datetime

# ---------------------------------------------------------------------
# Default eligibility norms (derived from institutional/AICTE-style rules).
# These are intentionally exposed as a plain dict so the Streamlit sidebar
# can let the user override them live (e.g. for a "what-if" analysis).
# ---------------------------------------------------------------------
DEFAULT_MIN_EXPERIENCE = {
    "Assistant Professor": 5,
    "Associate Professor": 8,
    "Professor": 12,
}


def academic_batch_reference_date(batch_label: str) -> datetime:
    """
    Convert an academic batch label like '2025-2026' into a concrete
    reference date used to compute "experience as of that batch".

    Convention used: experience is measured as on 1st July of the
    *starting* year of the batch (standard academic-year cutoff in India).
    Change this single function if your institution uses a different
    cutoff (e.g. 31st March or 31st December).
    """
    start_year = int(str(batch_label).split("-")[0])
    return datetime(start_year, 7, 1)


def compute_experience_as_of(df: pd.DataFrame, reference_date: datetime) -> pd.Series:
    """
    Recalculate each faculty member's experience (in years, 2 decimals)
    as of `reference_date`, using Date of Joining.

    This lets the dashboard answer "who is eligible for the 2027-2028
    batch?" even though the CSV's static 'Experience Years' column was
    only accurate as of when the sheet was prepared.
    """
    joining = pd.to_datetime(df["Date of Joining"], errors="coerce", dayfirst=False)
    delta_days = (reference_date - joining).dt.days
    experience_years = (delta_days / 365.25).round(2)
    return experience_years.clip(lower=0)


def determine_eligibility(df: pd.DataFrame, min_experience: dict) -> pd.Series:
    """
    Vectorised eligibility check: a faculty member is 'Eligible' if their
    (recalculated) experience meets the minimum required for their
    Designation. Unknown designations default to "Not Eligible".
    """
    required = df["Designation"].map(min_experience)
    is_eligible = df["Computed Experience"] >= required
    is_eligible = is_eligible.fillna(False)
    return is_eligible.map({True: "Eligible", False: "Not Eligible"})


def enrich_with_batch_eligibility(df: pd.DataFrame, batch_label: str, min_experience: dict) -> pd.DataFrame:
    """
    Returns a copy of df with two new columns:
      - 'Computed Experience'  : experience as of the selected batch
      - 'Batch Eligibility'    : Eligible / Not Eligible for that batch
    """
    out = df.copy()
    ref_date = academic_batch_reference_date(batch_label)
    out["Computed Experience"] = compute_experience_as_of(out, ref_date)
    out["Batch Eligibility"] = determine_eligibility(out, min_experience)
    return out


def student_faculty_ratio(total_students: int, eligible_faculty_count: int) -> float:
    """
    Standard Student:Faculty ratio = Total Students / Eligible Faculty.
    Returns None if there are zero eligible faculty (avoid div-by-zero).
    """
    if eligible_faculty_count <= 0:
        return None
    return round(total_students / eligible_faculty_count, 2)


def generate_batch_options(df: pd.DataFrame, span_back=3, span_forward=3):
    """
    Build a sensible list of academic-batch labels (e.g. '2023-2024')
    centered around the current year, so the sidebar dropdown always has
    relevant options regardless of the dataset's date range.
    """
    current_year = datetime.now().year
    years = range(current_year - span_back, current_year + span_forward + 1)
    return [f"{y}-{y+1}" for y in years]
