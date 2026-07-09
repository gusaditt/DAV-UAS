import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ============================================================
# 1. PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="KopiSeru Marketing Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# 2. DESIGN TOKENS
#    Dominant palette: brown + cream. Green/red only for deltas.
# ============================================================
BROWN_900 = "#3E2723"
BROWN_800 = "#4A2C22"
BROWN_700 = "#5D4037"
BROWN_600 = "#6D4C41"
BROWN_500 = "#8D6E63"
BROWN_400 = "#A1887F"
BROWN_300 = "#BCAAA4"
BROWN_200 = "#D7CCC8"
BROWN_100 = "#EFEBE9"
CREAM_BG = "#F8F4EF"
CARD_WHITE = "#FFFFFF"
BORDER = "#E9E1D9"
GRID = "#F2ECE6"
GREEN = "#2E7D32"
GREEN_BG = "#E8F5E9"
RED = "#C62828"
RED_BG = "#FFEBEE"

# ============================================================
# 3. GLOBAL CSS
#    Goal: one-screen dashboard, no vertical scroll, white cards.
# ============================================================
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {{
    --bg: {CREAM_BG};
    --card: {CARD_WHITE};
    --brown-900: {BROWN_900};
    --brown-700: {BROWN_700};
    --brown-500: {BROWN_500};
    --border: {BORDER};
    --green: {GREEN};
    --green-bg: {GREEN_BG};
    --red: {RED};
    --red-bg: {RED_BG};
}}

/* ---------- Hide Streamlit chrome ---------- */
#MainMenu, footer, header {{ visibility: hidden !important; }}
[data-testid="stSidebar"],
[data-testid="collapsedControl"] {{ display: none !important; }}

/* ---------- Hide all scrollbars globally (Chrome/Safari/Edge/Firefox) ---------- */
::-webkit-scrollbar {{
    display: none !important;
    width: 0 !important;
    height: 0 !important;
}}

* {{
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
}}

/* ---------- Hard no-scroll viewport ---------- */
html, body {{
    width: 100% !important;
    height: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    background: var(--bg) !important;
}}

[data-testid="stApp"],
[data-testid="stAppViewContainer"],
.main {{
    width: 100vw !important;
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: hidden !important;
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
}}

[data-testid="stAppViewContainer"] > .main {{
    overflow: hidden !important;
}}

.block-container {{
    width: 100% !important;
    max-width: 100% !important;
    height: 100vh !important;
    max-height: 100vh !important;
    padding: 0.55rem 1.0rem 0.40rem 1.0rem !important;
    overflow: hidden !important;
}}

/* Streamlit layout spacing and overlap prevention */
[data-testid="stVerticalBlock"],
.stVerticalBlock {{
    gap: 0.42rem !important;
}}

/* Force all layout and element containers to never shrink vertically, preventing overlaps */
[data-testid="stVerticalBlock"] > div,
.stVerticalBlock > div,
div[data-testid="element-container"],
.element-container,
div[data-testid="stHorizontalBlock"],
.stHorizontalBlock {{
    flex-shrink: 0 !important;
}}

div[data-testid="stHorizontalBlock"],
.stHorizontalBlock {{
    gap: 0.62rem !important;
    align-items: stretch !important;
}}

/* Force chart header containers to never shrink and collapse, preventing Plotly overlap */
div[data-testid="element-container"]:has(.chart-title),
div[data-testid="element-container"]:has(.chart-title) > div,
div[data-testid="element-container"]:has(.chart-title) div[data-testid="stMarkdownContainer"] {{
    min-height: max-content !important;
    height: auto !important;
    flex-shrink: 0 !important;
}}

/* ---------- Header ---------- */
.dashboard-head {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 48px;
    padding: 0.05rem 0;
    margin-top: 14px;
}}

.dashboard-title {{
    color: var(--brown-900);
    font-size: 1.32rem;
    line-height: 1.10;
    font-weight: 800;
    letter-spacing: -0.45px;
    white-space: nowrap;
}}

.dashboard-subtitle {{
    color: var(--brown-500);
    font-size: 0.64rem;
    line-height: 1.10;
    font-weight: 400;
    margin-top: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

/* ---------- Selectboxes / filter cards ---------- */
div[data-testid="stSelectbox"] {{
    margin: 0 !important;
}}

div[data-testid="stSelectbox"] {{
    margin-top: -3px !important;
    margin-bottom: -3px !important;
}}

div[data-testid="stSelectbox"] label {{
    margin: 0 0 1px 0 !important;
    padding: 0 !important;
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}}

div[data-testid="stSelectbox"] label p {{
    color: var(--brown-500) !important;
    font-size: 0.62rem !important;
    line-height: 1 !important;
    font-weight: 800 !important;
    letter-spacing: 0.30px !important;
    text-transform: uppercase !important;
    white-space: nowrap !important;
    text-align: center !important;
}}

div[data-baseweb="select"] > div {{
    min-height: 30px !important;
    height: 30px !important;
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 9px !important;
    box-shadow: 0 1px 3px rgba(62,39,35,0.035) !important;
    padding-left: 0.08rem !important;
    overflow: hidden !important;
}}

div[data-baseweb="select"] > div > div {{
    padding-top: 5px !important;
    padding-bottom: 0 !important;
    display: flex !important;
    align-items: center !important;
    height: 100% !important;
}}

div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[data-baseweb="select"] div {{
    font-family: 'Inter', sans-serif !important;
}}

div[data-baseweb="select"] span {{
    color: var(--brown-900) !important;
    font-size: 0.66rem !important;
    line-height: 1.2 !important;
    font-weight: 500 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}}

ul[role="listbox"] {{
    font-size: 0.68rem !important;
}}

/* ---------- KPI cards ---------- */
div[data-testid="stHorizontalBlock"]:has(.kpi-card) {{
    min-height: 90px !important;
    height: 90px !important;
    margin-bottom: 0.15rem !important;
}}

.kpi-card {{
    height: 78px;
    min-height: 78px;
    box-sizing: border-box;
    background: #FFFFFF !important;
    opacity: 1 !important;
    border: 1px solid var(--border);
    border-radius: 11px;
    box-shadow: 0 2px 8px rgba(62,39,35,0.045);
    padding: 0.56rem 0.70rem;
    display: flex;
    align-items: center;
    gap: 0.62rem;
    overflow: hidden;
}}

.kpi-icon-wrap {{
    flex: 0 0 42px;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--brown-700);
    background: #F5EADF;
    font-size: 1.10rem;
}}

.kpi-content {{
    flex: 1 1 auto;
    min-width: 0;
}}

.kpi-label {{
    color: var(--brown-500);
    font-size: 0.57rem;
    line-height: 1.05;
    font-weight: 700;
    letter-spacing: 0.30px;
    text-transform: uppercase;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.kpi-main-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.35rem;
    margin-top: 4px;
}}

.kpi-value {{
    color: var(--brown-900);
    font-size: 1.10rem;
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: -0.25px;
    white-space: nowrap;
}}

.kpi-delta-up,
.kpi-delta-down {{
    flex: 0 0 auto;
    font-size: 0.56rem;
    line-height: 1;
    font-weight: 700;
    padding: 4px 6px;
    border-radius: 6px;
    white-space: nowrap;
}}

.kpi-delta-up {{
    color: var(--green);
    background: var(--green-bg);
}}

.kpi-delta-down {{
    color: var(--red);
    background: var(--red-bg);
}}

.kpi-delta-neutral {{
    flex: 0 0 auto;
    color: var(--brown-500);
    background: #F5F1ED;
    font-size: 0.54rem;
    line-height: 1;
    font-weight: 600;
    padding: 4px 6px;
    border-radius: 6px;
    white-space: nowrap;
}}
.kpi-caption {{
    color: #A1887F;
    font-size: 0.51rem;
    line-height: 1;
    margin-top: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

/* ---------- Solid white chart cards ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: #FFFFFF !important;
    background-color: #FFFFFF !important;
    opacity: 1 !important;
    border: 1px solid var(--border) !important;
    border-radius: 11px !important;
    box-shadow: 0 2px 8px rgba(62,39,35,0.045) !important;
    padding: 0.46rem 0.62rem 0.22rem 0.62rem !important;
    overflow: hidden !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] > div,
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {{
    background: #FFFFFF !important;
    background-color: #FFFFFF !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
}}

/* Ensure the elements inside vertical block use flex stretch */
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] > div {{
    flex-shrink: 0 !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="element-container"]:has(.chart-title) {{
    flex: 0 0 auto !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="element-container"]:has(.stPlotlyChart),
div[data-testid="stVerticalBlockBorderWrapper"] .stPlotlyChart,
div[data-testid="stVerticalBlockBorderWrapper"] .stPlotlyChart > div,
div[data-testid="stVerticalBlockBorderWrapper"] iframe {{
    flex: 1 1 auto !important;
    min-height: 0 !important;
    height: 100% !important;
    max-height: 100% !important;
}}

.chart-title {{
    color: var(--brown-900);
    font-size: 0.74rem;
    line-height: 1.10;
    font-weight: 750;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.chart-subtitle {{
    color: #A1887F;
    font-size: 0.54rem;
    line-height: 1.10;
    margin-top: 2px;
    margin-bottom: 0.38rem;
}}

.stPlotlyChart {{
    margin-top: 0.55rem !important;
}}

.stPlotlyChart,
.stPlotlyChart > div {{
    background: #FFFFFF !important;
    border-radius: 7px;
    overflow: hidden !important;
}}

/* Prevent accidental extra spacing from empty paragraphs */
p:empty {{ display: none !important; }}

/* ---------- Responsive compression for short laptop screens ---------- */
@media (max-height: 850px) {{
    .block-container {{
        padding-top: 0.35rem !important;
        padding-bottom: 0.28rem !important;
    }}
    [data-testid="stVerticalBlock"] {{ gap: 0.30rem !important; }}
    div[data-testid="stHorizontalBlock"] {{ gap: 0.50rem !important; }}
    .dashboard-head {{ min-height: 42px; }}
    .dashboard-title {{ font-size: 1.16rem; }}
    .dashboard-subtitle {{ font-size: 0.57rem; }}
    div[data-testid="stHorizontalBlock"]:has(.kpi-card) {{
        min-height: 78px !important;
        height: 78px !important;
        margin-bottom: 0.10rem !important;
    }}
    .kpi-card {{ height: 68px; min-height: 68px; padding: 0.42rem 0.58rem; }}
    .kpi-icon-wrap {{ width: 36px; height: 36px; flex-basis: 36px; font-size: 0.95rem; }}
    .kpi-value {{ font-size: 0.98rem; }}
    .kpi-label {{ font-size: 0.52rem; }}
    .chart-title {{ font-size: 0.68rem; }}
    .chart-subtitle {{ font-size: 0.50rem; margin-bottom: 0.24rem; }}
    .stPlotlyChart {{ margin-top: 0.40rem !important; }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        padding: 0.30rem 0.45rem 0.15rem 0.45rem !important;
    }}
}}

@media (max-height: 720px) {{
    .dashboard-head {{ min-height: 34px; margin-top: 8px; }}
    div[data-testid="stHorizontalBlock"]:has(.kpi-card) {{
        min-height: 72px !important;
        height: 72px !important;
        margin-bottom: 0.05rem !important;
    }}
    .kpi-card {{ height: 64px; min-height: 64px; }}
    .kpi-caption {{ font-size: 0.48rem; margin-top: 2px; }}
    .stPlotlyChart {{ margin-top: 0.30rem !important; }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        padding: 0.20rem 0.35rem 0.10rem 0.35rem !important;
    }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 4. DATA LOADING
# ============================================================
DEFAULT_DATA_PATHS = [
    "coffee_shop_data_cleaned_final (7) (1).xlsx",
    "coffe_shop_final.xlsx",
    "coffee_shop_final.xlsx",
]


def resolve_excel_path() -> Path:
    """Resolve the Excel source without hard-failing on one filename."""
    env_path = os.getenv("KOPISERU_DATA_PATH")
    candidates = []
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(Path(p) for p in DEFAULT_DATA_PATHS)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    # Last fallback: first xlsx in current folder
    xlsx_files = sorted(Path(".").glob("*.xlsx"))
    if xlsx_files:
        return xlsx_files[0]

    raise FileNotFoundError(
        "File Excel tidak ditemukan. Letakkan dataset .xlsx di folder yang sama "
        "dengan app.py atau set environment variable KOPISERU_DATA_PATH."
    )


@st.cache_data(show_spinner=False)
def load_data(path_str: str) -> pd.DataFrame:
    data = pd.read_excel(path_str)

    required_cols = {
        "date",
        "branch_name",
        "branch_city",
        "branch_type",
        "total_transactions",
        "total_revenue",
        "avg_ticket_size",
        "total_cups_sold",
        "top_selling_category",
        "dine_in_percent",
        "delivery_percent",
        "takeaway_percent",
        "promo_active",
        "promo_type",
        "is_weekend",
    }
    missing = sorted(required_cols - set(data.columns))
    if missing:
        raise ValueError(f"Kolom dataset belum lengkap: {', '.join(missing)}")

    data = data.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data = data.dropna(subset=["date"])

    # Standardized helper dimensions
    data["year"] = data["date"].dt.year.astype(int)
    data["month_period"] = data["date"].dt.to_period("M")
    data["month_label"] = data["date"].dt.strftime("%b %Y")
    data["promo_active"] = data["promo_active"].fillna(False).astype(bool)
    data["promo_status"] = np.where(data["promo_active"], "Promo", "Non Promo")
    data["day_type"] = np.where(data["is_weekend"].fillna(False).astype(bool), "Weekend", "Weekday")
    data["promo_type"] = data["promo_type"].fillna("No Promo")

    # Numeric safety
    numeric_cols = [
        "total_transactions",
        "total_revenue",
        "avg_ticket_size",
        "total_cups_sold",
        "dine_in_percent",
        "delivery_percent",
        "takeaway_percent",
    ]
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    return data


try:
    EXCEL_PATH = resolve_excel_path()
    df = load_data(str(EXCEL_PATH))
except Exception as exc:
    st.error(f"Gagal memuat dataset: {exc}")
    st.stop()

# ============================================================
# 5. FORMAT & ANALYTIC HELPERS
# ============================================================
def format_rupiah(value: float) -> str:
    value = float(value or 0)
    abs_v = abs(value)
    sign = "-" if value < 0 else ""
    if abs_v >= 1_000_000_000_000:
        return f"{sign}Rp {abs_v / 1_000_000_000_000:.1f} T"
    if abs_v >= 1_000_000_000:
        return f"{sign}Rp {abs_v / 1_000_000_000:.1f} B"
    if abs_v >= 1_000_000:
        return f"{sign}Rp {abs_v / 1_000_000:.1f} M"
    if abs_v >= 1_000:
        return f"{sign}Rp {abs_v / 1_000:.1f} K"
    return f"{sign}Rp {abs_v:,.0f}"


def format_number(value: float) -> str:
    value = float(value or 0)
    abs_v = abs(value)
    sign = "-" if value < 0 else ""
    if abs_v >= 1_000_000_000:
        return f"{sign}{abs_v / 1_000_000_000:.1f} B"
    if abs_v >= 1_000_000:
        return f"{sign}{abs_v / 1_000_000:.2f} M"
    if abs_v >= 1_000:
        return f"{sign}{abs_v / 1_000:.1f} K"
    return f"{sign}{abs_v:,.0f}"


def calc_delta(current: float, previous: float | None) -> float | None:
    if previous is None or pd.isna(previous) or previous == 0:
        return None
    return ((current - previous) / previous) * 100


def weighted_ticket(data: pd.DataFrame) -> float:
    transactions = data["total_transactions"].sum()
    if transactions == 0:
        return 0.0
    return data["total_revenue"].sum() / transactions


def html_kpi(icon: str, label: str, value: str, delta: float | None, caption: str) -> str:
    if delta is None:
        delta_html = '<span class="kpi-delta-neutral">—</span>'
    elif delta >= 0:
        delta_html = f'<span class="kpi-delta-up">▲ {delta:.1f}%</span>'
    else:
        delta_html = f'<span class="kpi-delta-down">▼ {abs(delta):.1f}%</span>'

    return f"""
    <div class="kpi-card">
        <div class="kpi-icon-wrap">{icon}</div>
        <div class="kpi-content">
            <div class="kpi-label">{label}</div>
            <div class="kpi-main-row">
                <div class="kpi-value">{value}</div>
                {delta_html}
            </div>
            <div class="kpi-caption">{caption}</div>
        </div>
    </div>
    """


def solid_plot_layout(fig: go.Figure, height: int) -> go.Figure:
    """Apply consistent white-card Plotly styling."""
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor=CARD_WHITE,
        plot_bgcolor=CARD_WHITE,
        font=dict(family="Inter", size=9, color=BROWN_700),
        hoverlabel=dict(
            bgcolor=CARD_WHITE,
            bordercolor=BORDER,
            font=dict(family="Inter", size=10, color=BROWN_900),
        ),
    )
    return fig


# ============================================================
# 6. HEADER + FILTERS
#    No search bar. Compact labels to avoid clipping.
# ============================================================
header_col, fy_col, branch_col, city_col, type_col, promo_col = st.columns(
    [4.2, 1.15, 1.45, 1.25, 1.40, 1.45]
)

with header_col:
    st.markdown(
        """
        <div class="dashboard-head">
            <div class="dashboard-title">KopiSeru Marketing Dashboard</div>
            <div class="dashboard-subtitle">Revenue, customer activity, channel mix and actionable marketing performance</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Initialize session state for filters
if "selected_year" not in st.session_state:
    st.session_state.selected_year = "All Years"
if "selected_branch" not in st.session_state:
    st.session_state.selected_branch = "All Branches"
if "selected_city" not in st.session_state:
    st.session_state.selected_city = "All Cities"
if "selected_type" not in st.session_state:
    st.session_state.selected_type = "All Types"
if "selected_promo" not in st.session_state:
    st.session_state.selected_promo = "All Promos"

# Auto-set City and Branch Type if a specific branch is selected
if st.session_state.selected_branch != "All Branches":
    branch_rows = df[df["branch_name"] == st.session_state.selected_branch]
    if not branch_rows.empty:
        st.session_state.selected_city = branch_rows["branch_city"].iloc[0]
        st.session_state.selected_type = branch_rows["branch_type"].iloc[0]

# Compute options dynamically based on all OTHER active selections
# 1. Year options
df_year = df.copy()
if st.session_state.selected_branch != "All Branches":
    df_year = df_year[df_year["branch_name"] == st.session_state.selected_branch]
if st.session_state.selected_city != "All Cities":
    df_year = df_year[df_year["branch_city"] == st.session_state.selected_city]
if st.session_state.selected_type != "All Types":
    df_year = df_year[df_year["branch_type"] == st.session_state.selected_type]
if st.session_state.selected_promo != "All Promos":
    df_year = df_year[df_year["promo_type"] == st.session_state.selected_promo]
available_years = sorted(df_year["year"].dropna().unique().astype(int).tolist())
year_options = ["All Years"] + [str(y) for y in available_years]

# 2. Branch options
df_branch = df.copy()
if st.session_state.selected_year != "All Years":
    df_branch = df_branch[df_branch["year"] == int(st.session_state.selected_year)]
if st.session_state.selected_city != "All Cities":
    df_branch = df_branch[df_branch["branch_city"] == st.session_state.selected_city]
if st.session_state.selected_type != "All Types":
    df_branch = df_branch[df_branch["branch_type"] == st.session_state.selected_type]
if st.session_state.selected_promo != "All Promos":
    df_branch = df_branch[df_branch["promo_type"] == st.session_state.selected_promo]
available_branches = sorted(df_branch["branch_name"].dropna().astype(str).unique().tolist())
branch_options = ["All Branches"] + available_branches

# 3. City options
df_city = df.copy()
if st.session_state.selected_year != "All Years":
    df_city = df_city[df_city["year"] == int(st.session_state.selected_year)]
if st.session_state.selected_branch != "All Branches":
    df_city = df_city[df_city["branch_name"] == st.session_state.selected_branch]
if st.session_state.selected_type != "All Types":
    df_city = df_city[df_city["branch_type"] == st.session_state.selected_type]
if st.session_state.selected_promo != "All Promos":
    df_city = df_city[df_city["promo_type"] == st.session_state.selected_promo]
available_cities = sorted(df_city["branch_city"].dropna().astype(str).unique().tolist())
city_options = ["All Cities"] + available_cities

# 4. Branch Type options
df_type = df.copy()
if st.session_state.selected_year != "All Years":
    df_type = df_type[df_type["year"] == int(st.session_state.selected_year)]
if st.session_state.selected_branch != "All Branches":
    df_type = df_type[df_type["branch_name"] == st.session_state.selected_branch]
if st.session_state.selected_city != "All Cities":
    df_type = df_type[df_type["branch_city"] == st.session_state.selected_city]
if st.session_state.selected_promo != "All Promos":
    df_type = df_type[df_type["promo_type"] == st.session_state.selected_promo]
available_types = sorted(df_type["branch_type"].dropna().astype(str).unique().tolist())
type_options = ["All Types"] + available_types

# 5. Promo Type options
df_promo = df.copy()
if st.session_state.selected_year != "All Years":
    df_promo = df_promo[df_promo["year"] == int(st.session_state.selected_year)]
if st.session_state.selected_branch != "All Branches":
    df_promo = df_promo[df_promo["branch_name"] == st.session_state.selected_branch]
if st.session_state.selected_city != "All Cities":
    df_promo = df_promo[df_promo["branch_city"] == st.session_state.selected_city]
if st.session_state.selected_type != "All Types":
    df_promo = df_promo[df_promo["branch_type"] == st.session_state.selected_type]
available_promos = sorted([p for p in df_promo["promo_type"].dropna().astype(str).unique().tolist() if p != "No Promo"])
promo_options = ["All Promos"] + available_promos

# Validate selections against available options (reset to "All ..." if invalid)
if st.session_state.selected_year not in year_options:
    st.session_state.selected_year = "All Years"
if st.session_state.selected_branch not in branch_options:
    st.session_state.selected_branch = "All Branches"
if st.session_state.selected_city not in city_options:
    st.session_state.selected_city = "All Cities"
if st.session_state.selected_type not in type_options:
    st.session_state.selected_type = "All Types"
if st.session_state.selected_promo not in promo_options:
    st.session_state.selected_promo = "All Promos"

with fy_col:
    selected_year = st.selectbox("Year", options=year_options, key="selected_year")
with branch_col:
    selected_branch = st.selectbox("Branch", options=branch_options, key="selected_branch")
with city_col:
    selected_city = st.selectbox("City", options=city_options, key="selected_city")
with type_col:
    selected_type = st.selectbox("Branch Type", options=type_options, key="selected_type")
with promo_col:
    selected_promo = st.selectbox("Promo Type", options=promo_options, key="selected_promo")

# ============================================================
# 7. APPLY FILTERS
# ============================================================
filtered = df.copy()

if selected_year != "All Years":
    filtered = filtered[filtered["year"] == int(selected_year)]
if selected_branch != "All Branches":
    filtered = filtered[filtered["branch_name"] == selected_branch]
if selected_city != "All Cities":
    filtered = filtered[filtered["branch_city"] == selected_city]
if selected_type != "All Types":
    filtered = filtered[filtered["branch_type"] == selected_type]
if selected_promo != "All Promos":
    filtered = filtered[filtered["promo_type"] == selected_promo]

if filtered.empty:
    st.warning("Tidak ada data untuk kombinasi filter yang dipilih.")
    st.stop()

# Previous year comparison, preserving non-year filters.
if selected_year != "All Years":
    previous = df[df["year"] == int(selected_year) - 1].copy()
    if selected_branch != "All Branches":
        previous = previous[previous["branch_name"] == selected_branch]
    if selected_city != "All Cities":
        previous = previous[previous["branch_city"] == selected_city]
    if selected_type != "All Types":
        previous = previous[previous["branch_type"] == selected_type]
    if selected_promo != "All Promos":
        previous = previous[previous["promo_type"] == selected_promo]
    comparison_caption = "vs previous year"
else:
    previous = pd.DataFrame()
    comparison_caption = ""

# ============================================================
# 8. KPI CALCULATIONS
# ============================================================
total_revenue = filtered["total_revenue"].sum()
total_transactions = filtered["total_transactions"].sum()
total_cups = filtered["total_cups_sold"].sum()
avg_ticket = weighted_ticket(filtered)

if not previous.empty:
    prev_revenue = previous["total_revenue"].sum()
    prev_transactions = previous["total_transactions"].sum()
    prev_cups = previous["total_cups_sold"].sum()
    prev_ticket = weighted_ticket(previous)

    delta_revenue = calc_delta(total_revenue, prev_revenue)
    delta_transactions = calc_delta(total_transactions, prev_transactions)
    delta_cups = calc_delta(total_cups, prev_cups)
    delta_ticket = calc_delta(avg_ticket, prev_ticket)
else:
    delta_revenue = None
    delta_transactions = None
    delta_cups = None
    delta_ticket = None

# ============================================================
# 9. PART 1 — KPI CARDS
# ============================================================
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        html_kpi("💰", "Revenue", format_rupiah(total_revenue), delta_revenue, comparison_caption),
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        html_kpi("👥", "Total Transactions", format_number(total_transactions), delta_transactions, comparison_caption),
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        html_kpi("🎟️", "Avg Ticket Size", format_rupiah(avg_ticket), delta_ticket, comparison_caption),
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        html_kpi("☕", "Cups Sold", format_number(total_cups), delta_cups, comparison_caption),
        unsafe_allow_html=True,
    )

# ============================================================
# 10. PART 2 — MIDDLE ROW
#     A. Monthly Performance Overview
#     B. Customer Channel Mix
# ============================================================
mid_left, mid_right = st.columns([5.1, 3.0])

# ---------- A. Performance Overview ----------
with mid_left:
    with st.container(border=True):
        st.markdown(
            '<div class="chart-title">Performance Overview</div>'
            '<div class="chart-subtitle">Monthly trend for Revenue and Operating Cost<br>&nbsp;</div>',
            unsafe_allow_html=True,
        )

        monthly = (
            filtered.groupby("month_period", as_index=False)
            .agg(
                revenue=("total_revenue", "sum"),
                op_cost=("operating_cost", "sum"),
            )
            .sort_values("month_period")
        )
        monthly["date"] = monthly["month_period"].dt.to_timestamp()

        fig_perf = go.Figure()

        fig_perf.add_trace(
            go.Scatter(
                x=monthly["date"],
                y=monthly["revenue"],
                name="Revenue (Rp)",
                mode="lines+markers",
                line=dict(color=BROWN_800, width=2.0),
                marker=dict(size=4.5, color=BROWN_800),
                fill="tozeroy",
                fillcolor="rgba(78,52,46,0.045)",
                hovertemplate="Revenue: Rp %{y:,.0f}<extra></extra>",
            )
        )

        fig_perf.add_trace(
            go.Scatter(
                x=monthly["date"],
                y=monthly["op_cost"],
                name="Operating Cost (Rp)",
                mode="lines+markers",
                line=dict(color=BROWN_500, width=1.7, dash="dot"),
                marker=dict(size=4.0, color=BROWN_500),
                hovertemplate="Operating Cost: Rp %{y:,.0f}<extra></extra>",
            )
        )

        solid_plot_layout(fig_perf, 160)
        fig_perf.update_layout(
            margin=dict(l=8, r=8, t=32, b=8),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,
                xanchor="center",
                x=0.5,
                font=dict(size=8),
                bgcolor="rgba(255,255,255,0)",
            ),
            hovermode="x unified",
        )
        fig_perf.update_xaxes(
            showgrid=False,
            showline=True,
            linecolor=BORDER,
            tickformat="%b\n%Y",
            tickfont=dict(size=8, color=BROWN_700),
            nticks=min(12, max(len(monthly), 2)),
            fixedrange=True,
        )
        fig_perf.update_yaxes(
            showgrid=True,
            gridcolor=GRID,
            zeroline=False,
            tickfont=dict(size=8),
            tickformat="~s",
            title_text="",
            fixedrange=True,
        )

        st.plotly_chart(
            fig_perf,
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )

# ---------- B. Customer Channel Mix ----------
with mid_right:
    with st.container(border=True):
        st.markdown(
            '<div class="chart-title">Customer Channel Mix</div>'
            '<div class="chart-subtitle">Estimated share of transactions by customer channel<br>&nbsp;</div>',
            unsafe_allow_html=True,
        )

        # More valid than "revenue by channel": estimate transaction counts
        # because dataset contains channel percentages, not actual channel revenue.
        channel_data = pd.DataFrame(
            {
                "Channel": ["Takeaway", "Dine-In", "Delivery"],
                "Transactions": [
                    (filtered["takeaway_percent"] / 100 * filtered["total_transactions"]).sum(),
                    (filtered["dine_in_percent"] / 100 * filtered["total_transactions"]).sum(),
                    (filtered["delivery_percent"] / 100 * filtered["total_transactions"]).sum(),
                ],
            }
        )

        fig_channel = go.Figure(
            go.Pie(
                labels=channel_data["Channel"],
                values=channel_data["Transactions"],
                hole=0.57,
                sort=False,
                marker=dict(colors=[BROWN_800, BROWN_500, "#E2C5A8"], line=dict(color=CARD_WHITE, width=1.2)),
                textinfo="percent",
                textposition="inside",
                textfont=dict(size=9, family="Inter", color=CARD_WHITE),
                hovertemplate="<b>%{label}</b><br>Estimated transactions: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
            )
        )
        solid_plot_layout(fig_channel, 160)
        fig_channel.update_layout(
            margin=dict(l=2, r=2, t=28, b=4),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.52,
                xanchor="left",
                x=0.79,
                font=dict(size=8.5, color=BROWN_700),
            ),
            annotations=[
                dict(
                    text=f"<b>{format_number(total_transactions)}</b><br><span style='font-size:8px'>Transactions</span>",
                    x=0.50,
                    y=0.50,
                    showarrow=False,
                    align="center",
                    font=dict(size=10, color=BROWN_900, family="Inter"),
                )
            ],
        )

        st.plotly_chart(
            fig_channel,
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )

# ============================================================
# 11. PART 3 — BOTTOM ROW, THREE ACTIONABLE MARKETING CHARTS
# ============================================================
b1, b2, b3 = st.columns(3)

# ---------- A. Promo vs Non Promo ----------
with b1:
    with st.container(border=True):
        st.markdown(
            '<div class="chart-title">Promo vs Non Promo</div>'
            '<div class="chart-subtitle">Average revenue per branch-day<br>&nbsp;</div>',
            unsafe_allow_html=True,
        )

        promo_perf = (
            filtered.groupby("promo_status", as_index=False)
            .agg(avg_revenue=("total_revenue", "mean"))
        )
        promo_order = ["Promo", "Non Promo"]
        promo_perf["promo_status"] = pd.Categorical(
            promo_perf["promo_status"], categories=promo_order, ordered=True
        )
        promo_perf = promo_perf.sort_values("promo_status")

        fig_promo = go.Figure(
            go.Bar(
                x=promo_perf["promo_status"].astype(str),
                y=promo_perf["avg_revenue"],
                marker=dict(color=[BROWN_800, "#D9B996"][: len(promo_perf)], cornerradius=5),
                text=[format_rupiah(v) for v in promo_perf["avg_revenue"]],
                textposition="outside",
                textfont=dict(size=8.5, color=BROWN_900, family="Inter"),
                hovertemplate="<b>%{x}</b><br>Avg revenue / branch-day: Rp %{y:,.0f}<extra></extra>",
            )
        )
        solid_plot_layout(fig_promo, 150)
        max_promo = promo_perf["avg_revenue"].max() if not promo_perf.empty else 1
        fig_promo.update_layout(
            margin=dict(l=5, r=5, t=32, b=4),
            showlegend=False,
            xaxis=dict(showgrid=False, showline=True, linecolor=BORDER, tickfont=dict(size=8.5)),
            yaxis=dict(
                showgrid=True,
                gridcolor=GRID,
                zeroline=False,
                tickformat="~s",
                tickfont=dict(size=8),
                range=[0, max_promo * 1.25],
            ),
        )
        st.plotly_chart(fig_promo, use_container_width=True, config={"displayModeBar": False})

# ---------- B. Leading Category Performance ----------
with b2:
    with st.container(border=True):
        st.markdown(
            '<div class="chart-title">Top Category Performance</div>'
            '<div class="chart-subtitle">Revenue when each category is recorded as the leading category<br>&nbsp;</div>',
            unsafe_allow_html=True,
        )

        cat_rev = (
            filtered.groupby("top_selling_category", as_index=False)
            .agg(revenue=("total_revenue", "sum"))
            .sort_values("revenue", ascending=True)
        )

        fig_cat = go.Figure(
            go.Bar(
                y=cat_rev["top_selling_category"],
                x=cat_rev["revenue"],
                orientation="h",
                marker=dict(color=BROWN_800, cornerradius=4),
                text=[format_rupiah(v) for v in cat_rev["revenue"]],
                textposition="outside",
                textfont=dict(size=7.8, color=BROWN_700, family="Inter"),
                hovertemplate="<b>%{y}</b><br>Associated revenue: Rp %{x:,.0f}<extra></extra>",
            )
        )
        solid_plot_layout(fig_cat, 150)
        max_cat = cat_rev["revenue"].max() if not cat_rev.empty else 1
        fig_cat.update_layout(
            margin=dict(l=5, r=62, t=28, b=4),
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                range=[0, max_cat * 1.28],
            ),
            yaxis=dict(showgrid=False, tickfont=dict(size=7.7, color=BROWN_700)),
        )
        st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})

# ---------- C. Weekday vs Weekend ----------
with b3:
    with st.container(border=True):
        st.markdown(
            '<div class="chart-title">Weekday vs Weekend Performance</div>'
            '<div class="chart-subtitle">Comparison of revenue, transactions and weighted ticket size<br>&nbsp;</div>',
            unsafe_allow_html=True,
        )

        rows = []
        for day_type in ["Weekday", "Weekend"]:
            part = filtered[filtered["day_type"] == day_type]
            rows.append(
                {
                    "day_type": day_type,
                    "avg_revenue": part["total_revenue"].mean() if not part.empty else 0,
                    "avg_transactions": part["total_transactions"].mean() if not part.empty else 0,
                    "avg_ticket": weighted_ticket(part) if not part.empty else 0,
                }
            )
        ww = pd.DataFrame(rows)

        metrics = ["Avg Revenue", "Avg Transactions", "Avg Ticket"]
        weekday_vals = [
            ww.loc[ww["day_type"] == "Weekday", "avg_revenue"].iloc[0],
            ww.loc[ww["day_type"] == "Weekday", "avg_transactions"].iloc[0],
            ww.loc[ww["day_type"] == "Weekday", "avg_ticket"].iloc[0],
        ]
        weekend_vals = [
            ww.loc[ww["day_type"] == "Weekend", "avg_revenue"].iloc[0],
            ww.loc[ww["day_type"] == "Weekend", "avg_transactions"].iloc[0],
            ww.loc[ww["day_type"] == "Weekend", "avg_ticket"].iloc[0],
        ]

        # Normalize each metric within its pair for visual comparability,
        # while showing actual values as labels/hover.
        max_pair = np.maximum(np.array(weekday_vals, dtype=float), np.array(weekend_vals, dtype=float))
        max_pair[max_pair == 0] = 1
        weekday_norm = np.array(weekday_vals) / max_pair * 100
        weekend_norm = np.array(weekend_vals) / max_pair * 100

        weekday_labels = [format_rupiah(weekday_vals[0]), format_number(weekday_vals[1]), format_rupiah(weekday_vals[2])]
        weekend_labels = [format_rupiah(weekend_vals[0]), format_number(weekend_vals[1]), format_rupiah(weekend_vals[2])]

        fig_ww = go.Figure()
        fig_ww.add_trace(
            go.Bar(
                x=metrics,
                y=weekday_norm,
                name="Weekday",
                marker=dict(color=BROWN_800, cornerradius=4),
                text=weekday_labels,
                customdata=weekday_vals,
                textposition="outside",
                textfont=dict(size=7.4, color=BROWN_900),
                hovertemplate="<b>Weekday · %{x}</b><br>Actual value: %{text}<extra></extra>",
            )
        )
        fig_ww.add_trace(
            go.Bar(
                x=metrics,
                y=weekend_norm,
                name="Weekend",
                marker=dict(color="#D9B996", cornerradius=4),
                text=weekend_labels,
                customdata=weekend_vals,
                textposition="outside",
                textfont=dict(size=7.4, color=BROWN_900),
                hovertemplate="<b>Weekend · %{x}</b><br>Actual value: %{text}<extra></extra>",
            )
        )
        solid_plot_layout(fig_ww, 150)
        fig_ww.update_layout(
            barmode="group",
            margin=dict(l=4, r=4, t=32, b=4),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.00,
                xanchor="left",
                x=0.0,
                font=dict(size=7.8),
            ),
            xaxis=dict(showgrid=False, tickfont=dict(size=7.4), showline=True, linecolor=BORDER),
            yaxis=dict(showgrid=True, gridcolor=GRID, showticklabels=False, zeroline=False, range=[0, 122]),
        )
        st.plotly_chart(fig_ww, use_container_width=True, config={"displayModeBar": False})

# ============================================================
# END
# ============================================================
