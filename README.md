# Faculty Eligibility & Student-Faculty Ratio Dashboard

An interactive Streamlit dashboard that determines faculty eligibility for a
given academic batch and computes the Student-Faculty Ratio, built with
Streamlit + Pandas + Plotly.

## Project Structure

```
faculty_dashboard/
├── app.py                  # Main Streamlit app (UI, layout, charts)
├── utils/
│   ├── __init__.py
│   ├── data_loader.py       # Reading/validating CSV or Excel input
│   ├── eligibility.py       # Eligibility rules & ratio calculations
│   └── styling.py           # CSS + KPI card / section-title helpers
├── data/
│   └── faculty_data.csv     # Your sample dataset (bundled for demo)
├── requirements.txt
└── README.md
```

Keeping the eligibility **rules** (`utils/eligibility.py`) separate from the
**UI** (`app.py`) means you can change the business logic — or unit test it —
without touching any Streamlit code.

## Setup

```bash
cd faculty_dashboard
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## How Eligibility Is Calculated

Your dataset already contained an `Eligibility` column, and reverse-engineering
it revealed a clean rule based on **Designation** and **years of experience**:

| Designation           | Minimum Experience Required |
|------------------------|------------------------------|
| Assistant Professor    | 5 years                      |
| Associate Professor    | 8 years                      |
| Professor              | 12 years                     |

These are set as `DEFAULT_MIN_EXPERIENCE` in `utils/eligibility.py`, but are
**fully editable from the sidebar** at runtime — useful if your professor
wants to test different norms (e.g. AICTE vs UGC vs university-specific).

### Why "Computed Experience" instead of just using the CSV's `Experience Years`?

The CSV's experience number is a snapshot from whenever the sheet was made.
But the assignment asks you to determine eligibility **for a specific
academic batch** (e.g. 2027-2028) — which may be in the future or past
relative to the sheet. So the app recalculates each faculty member's
experience from their `Date of Joining` up to a reference date tied to the
batch you select (1st July of the batch's starting year, a common Indian
academic-year convention — change `academic_batch_reference_date()` in
`eligibility.py` if your institution uses a different cutoff like 31 March).

This means:
- Selecting **2026-2027** shows who is eligible *today*.
- Selecting **2028-2029** shows who *will become* eligible in the future
  (as their experience naturally grows) — genuinely useful for planning.

## Student-Faculty Ratio

`Ratio = Total Students / Eligible Faculty`

The uploaded dataset only contains **faculty** records — there's no student
headcount column — so the app asks for **Total Students** as a sidebar input
(default 500, editable). The department-wise ratio chart splits that number
evenly across departments as an estimate; swap in real per-department
counts in `app.py` (search for `per_dept_students`) if you have them.

## Dashboard Features

- **KPI Cards**: Total Faculty, Eligible Faculty, Not Eligible, Total
  Students, Student:Faculty Ratio.
- **Sidebar Filters**: Department, Designation, Eligibility status,
  free-text search (name or Faculty ID), academic batch selector,
  editable experience norms, student-count input.
- **Charts (Plotly)**:
  - Faculty count by Department (bar)
  - Eligibility split (donut)
  - Designation distribution (donut)
  - Experience distribution by Designation (histogram)
  - Estimated Student-Faculty Ratio by Department (bar)
- **Searchable/sortable Faculty Table** with color-coded eligibility status
  and a CSV download button for the filtered view.

## Using Your Own Data

Upload any CSV/Excel with these columns (order doesn't matter):

```
Faculty ID, Faculty Name, Department, Designation, Date of Joining, Experience Years
```

An `Eligibility` column is not required — the app computes its own
`Batch Eligibility` per the norms above. `data_loader.py` will raise a clear
error if a required column is missing, and `validate_dataframe()` flags
duplicate IDs, unparseable dates, or missing experience values in a sidebar
warning panel.

## Extending This Project

- Add a second uploader for a student-count-by-department sheet and join it
  in for exact (not estimated) department-wise ratios.
- Add authentication (`streamlit-authenticator`) if this needs to be
  multi-user/protected.
- Persist filtered results/history to a database instead of just CSV export.
- Deploy for free on [Streamlit Community Cloud](https://streamlit.io/cloud)
  by pushing this folder to a GitHub repo and pointing it at `app.py`.

Author
Shirisha TS
Computer Science and Engineering (Data Science)
