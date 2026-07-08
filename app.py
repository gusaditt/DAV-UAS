from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


st.set_page_config(
    page_title="KopiSeru Marketing Dashboard",
    page_icon="coffee",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_PATH = Path(__file__).resolve().parent / "coffee_shop_data_cleaned_final (7).xlsx"

BRAND = "#13B981"
BROWN = "#7A5136"
BLUE = "#2F80ED"
ORANGE = "#F97316"
RED = "#C2412D"
DARK = "#111827"
MUTED = "#6B7280"
CARD = "#EAF2FF"
GRID = "#DDE7F5"
PALETTE = ["#13B981", "#2F80ED", "#F97316", "#7A5136", "#8B5CF6"]


@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="coffee_shop_data_cleaned_final ")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["year"] = df["date"].dt.year
    df["promo_flag"] = df["promo_active"].map({True: "Promo aktif", False: "Tanpa promo"})
    df["promo_type"] = df["promo_type"].fillna("Tanpa promo")
    df["gross_profit"] = df["total_revenue"] - df["operating_cost"]
    return df


def rupiah(value: float) -> str:
    if abs(value) >= 1_000_000_000:
        return f"Rp {value / 1_000_000_000:.1f} M"
    if abs(value) >= 1_000_000:
        return f"Rp {value / 1_000_000:.1f} jt"
    return f"Rp {value:,.0f}"


def number(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f} jt"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f} rb"
    return f"{value:,.0f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def growth(current: float, previous: float) -> tuple[str, str]:
    if previous == 0:
        return "0.0%", "#6B7280"
    value = (current - previous) / previous
    color = BRAND if value >= 0 else RED
    sign = "+" if value >= 0 else "-"
    return f"{sign}{abs(value) * 100:.1f}%", color


def growth_tuple(current: float, previous: float) -> tuple[float, str, str]:
    value = growth_value(current, previous)
    color = BRAND if value >= 0 else RED
    arrow = "▲" if value >= 0 else "▼"
    return value, f"{arrow} {abs(value) * 100:.1f}%", color


def growth_value(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return (current - previous) / previous


def sparkline_svg(values: pd.Series, color: str) -> str:
    series = pd.Series(values).fillna(0).tail(12)
    if series.empty:
        series = pd.Series([0, 0])
    if len(series) == 1:
        series = pd.concat([series, series], ignore_index=True)
    min_value = series.min()
    max_value = series.max()
    span = max(max_value - min_value, 1)
    width = 220
    height = 34
    step = width / (len(series) - 1)
    points = []
    for index, value in enumerate(series):
        x = index * step
        y = height - ((value - min_value) / span * (height - 8)) - 4
        points.append(f"{x:.1f},{y:.1f}")
    return f"""
    <svg class="sparkline" viewBox="0 0 {width} {height}" preserveAspectRatio="none">
        <polyline points="{' '.join(points)}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
    """


def apply_style() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800&display=swap');
        html, body, [data-testid="stAppViewContainer"], .stApp {
            height: 100vh;
            overflow: hidden;
        }
        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"] {
            display: none;
        }
        .stApp {
            background: linear-gradient(135deg, #E0F2FE 0%, #EFF6FF 48%, #DFF7EF 100%);
            color: #111827;
            font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        .block-container {
            max-width: 1450px;
            height: calc(100vh - 1rem);
            overflow: hidden;
            padding: 0.74rem 1.2rem;
            background: #FFFFFF;
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-radius: 22px;
            box-shadow: 0 24px 70px rgba(15, 23, 42, 0.16);
            margin-top: 0.5rem;
        }
        section[data-testid="stSidebar"] { display: none; }
        .top-nav {
            background: linear-gradient(180deg, #F8FAFC 0%, #EEF6FF 100%);
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 0.48rem 0.7rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.52rem;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        }
        .brand-wrap { display: flex; align-items: center; gap: 0.55rem; }
        .brand-dot {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #13B981;
            color: white;
            display: grid;
            place-items: center;
            font-weight: 800;
            font-size: 0.82rem;
        }
        .brand-name { font-weight: 800; font-size: 1rem; }
        .nav-link { color: #374151; margin-left: 1.05rem; font-size: 0.78rem; }
        .nav-link.active { color: #13B981; font-weight: 800; }
        .avatar {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #13B981;
            color: white;
            display: grid;
            place-items: center;
            font-size: 0.75rem;
            font-weight: 800;
        }
        .title-row {
            display: flex;
            justify-content: space-between;
            align-items: end;
            margin: 0.2rem 0 0.45rem;
        }
        .title-text h1 {
            font-size: 1.35rem;
            margin: 0;
            letter-spacing: 0;
        }
        .title-text p {
            margin: 0.12rem 0 0;
            color: #6B7280;
            font-size: 0.73rem;
        }
        .filter-wrap {
            display: flex;
            justify-content: flex-end;
            align-items: end;
            gap: 0.75rem;
            padding-top: 1.25rem;
        }
        .filter-pill {
            background: #EAF2FF;
            border: 1px solid #DCE7F7;
            border-radius: 12px;
            height: 38px;
            display: flex;
            align-items: center;
            padding: 0 0.75rem;
            color: #111827;
            font-size: 0.75rem;
        }
        .kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 0.66rem 0.78rem 0.48rem;
            height: 126px;
            box-sizing: border-box;
            margin-bottom: 0.35rem;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 18px 38px rgba(15, 23, 42, 0.12);
        }
        .kpi-card.highlight {
            border-color: rgba(19, 185, 129, 0.55);
            box-shadow: 0 18px 42px rgba(19, 185, 129, 0.16);
        }
        .kpi-top {
            display: flex;
            align-items: start;
            justify-content: space-between;
            margin-bottom: 0.28rem;
        }
        .kpi-icon {
            width: 32px;
            height: 32px;
            border-radius: 12px;
            display: grid;
            place-items: center;
            color: #FFFFFF;
            font-weight: 800;
            font-size: 0.9rem;
        }
        .kpi-delta { font-size: 0.72rem; font-weight: 800; }
        .kpi-value { font-size: 1.22rem; font-weight: 850; color: #111827; line-height: 1.05; }
        .kpi-label { color: #64748B; font-size: 0.68rem; margin-top: 0.18rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.02rem; }
        .kpi-compare { color: #94A3B8; font-size: 0.63rem; margin-top: 0.08rem; }
        .sparkline { width: 100%; height: 28px; margin-top: 0.18rem; opacity: 0.95; }
        .insights-card {
            background: linear-gradient(135deg, #F8FAFC 0%, #EEFDF6 100%);
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 0.58rem 0.75rem;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.07);
        }
        .insights-title { font-size: 0.78rem; font-weight: 850; color: #111827; margin-bottom: 0.25rem; }
        .insights-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.22rem 0.8rem; }
        .insight-item { color: #334155; font-size: 0.66rem; line-height: 1.18; }
        .panel-title { font-weight: 850; font-size: 0.9rem; margin-bottom: 0.1rem; }
        .panel-insight { color: #4B5563; font-size: 0.68rem; line-height: 1.18; }
        div[data-testid="stVerticalBlock"] { gap: 0.62rem; }
        div[data-testid="stHorizontalBlock"] { gap: 0.95rem; }
        div[data-testid="stPlotlyChart"] {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
            transition: transform 160ms ease, box-shadow 160ms ease;
        }
        div[data-testid="stPlotlyChart"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.11);
        }
        div[data-testid="stSelectbox"] > label,
        div[data-testid="stRadio"] > label {
            display: none;
        }
        div[data-baseweb="select"] > div {
            min-height: 38px;
            border-radius: 12px;
            background: #F8FAFC;
            border-color: #E2E8F0;
            font-size: 0.75rem;
        }
        div[role="radiogroup"] {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 0.16rem 0.2rem;
            gap: 0.15rem;
            min-height: 38px;
        }
        div[role="radiogroup"] label {
            background: transparent;
            border-radius: 9px;
            padding: 0.22rem 0.62rem;
            color: #111827;
            font-size: 0.75rem;
        }
        div[role="radiogroup"] label:has(input:checked) {
            background: #13B981;
            color: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def fig_style(fig: go.Figure, height: int, legend: bool = False, top_margin: int = 96) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        showlegend=legend,
        margin=dict(l=8, r=8, t=top_margin, b=10),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color=DARK, size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, title=None, tickfont=dict(size=10))
    fig.update_yaxes(gridcolor=GRID, title=None, tickfont=dict(size=10))
    return fig


def add_chart_title(fig: go.Figure, title: str, insight: str) -> go.Figure:
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b><br><span style='font-size:12px;color:#4B5563'>{insight}</span>",
            x=0.02,
            xanchor="left",
            y=0.90,
            yanchor="top",
            font=dict(size=15, color=DARK),
        )
    )
    return fig


def kpi_card(
    title: str,
    value: str,
    delta: str,
    delta_color: str,
    icon: str,
    icon_color: str,
    compare_text: str,
    sparkline: str,
    highlight: bool = False,
) -> None:
    highlight_class = " highlight" if highlight else ""
    st.markdown(
        f"""
        <div class="kpi-card{highlight_class}">
            <div class="kpi-top">
                <div class="kpi-icon" style="background:{icon_color};">{icon}</div>
                <div class="kpi-delta" style="color:{delta_color};">{delta}</div>
            </div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{title}</div>
            <div class="kpi-compare">{compare_text}</div>
            {sparkline}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_title_and_filters(df: pd.DataFrame) -> pd.DataFrame:
    years = [str(year) for year in sorted(df["year"].unique())] + ["Semua"]
    campaigns = ["All Coffee Campaign"] + sorted(
        campaign for campaign in df["promo_type"].dropna().unique() if campaign != "Tanpa promo"
    )
    periods = ["Full Year", "Q1", "Q2", "Q3", "Q4"]

    title_left, title_right = st.columns([1.05, 1.35])
    with title_left:
        st.markdown(
            """
            <div class="title-text">
                <h1>Analytics Dashboard</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
        selected_campaign = st.selectbox("Campaign", campaigns, label_visibility="collapsed")

    with title_right:
        c1, c2 = st.columns([1.7, 0.9])
        with c1:
            selected_year = st.radio("Tahun", years, horizontal=True, label_visibility="collapsed")
        with c2:
            selected_period = st.selectbox("Periode", periods, label_visibility="collapsed")

    result = df.copy()
    if selected_campaign != "All Coffee Campaign":
        result = result[result["promo_type"] == selected_campaign]
    if selected_year != "Semua":
        result = result[result["year"] == int(selected_year)]
    if selected_period != "Full Year":
        quarter = int(selected_period.replace("Q", ""))
        result = result[result["date"].dt.quarter == quarter]
    return result


def metric_delta(df: pd.DataFrame, metric: str) -> tuple[str, str]:
    yearly = df.groupby("year")[metric].sum().sort_index()
    if len(yearly) < 2:
        return "+0.0%", BRAND
    return growth(yearly.iloc[-1], yearly.iloc[-2])


def build_dashboard(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("Tidak ada data pada filter ini. Pilih kombinasi lain.")
        return

    revenue = df["total_revenue"].sum()
    cost = df["operating_cost"].sum()
    profit = revenue - cost
    margin = profit / revenue if revenue else 0
    cups = df["total_cups_sold"].sum()
    satisfaction = df["customer_satisfaction"].mean()

    monthly_kpi = (
        df.groupby("month", as_index=False)
        .agg(
            revenue=("total_revenue", "sum"),
            profit=("gross_profit", "sum"),
            cups=("total_cups_sold", "sum"),
        )
        .sort_values("month")
    )
    monthly_kpi["margin"] = monthly_kpi["profit"] / monthly_kpi["revenue"].where(monthly_kpi["revenue"] != 0)

    yearly = (
        df.assign(margin_value=df["gross_profit"] / df["total_revenue"].where(df["total_revenue"] != 0))
        .groupby("year")
        .agg(
            revenue=("total_revenue", "sum"),
            profit=("gross_profit", "sum"),
            cups=("total_cups_sold", "sum"),
            margin=("margin_value", "mean"),
        )
        .sort_index()
    )
    if len(yearly) >= 2:
        rev_growth, rev_delta, rev_color = growth_tuple(yearly["revenue"].iloc[-1], yearly["revenue"].iloc[-2])
        profit_growth, profit_delta, profit_color = growth_tuple(yearly["profit"].iloc[-1], yearly["profit"].iloc[-2])
        cup_growth, cup_delta, cup_color = growth_tuple(yearly["cups"].iloc[-1], yearly["cups"].iloc[-2])
        margin_growth, margin_delta, margin_color = growth_tuple(yearly["margin"].iloc[-1], yearly["margin"].iloc[-2])
    else:
        rev_growth, rev_delta, rev_color = 0, "▲ 0.0%", BRAND
        profit_growth, profit_delta, profit_color = 0, "▲ 0.0%", BRAND
        cup_growth, cup_delta, cup_color = 0, "▲ 0.0%", BRAND
        margin_growth, margin_delta, margin_color = 0, "▲ 0.0%", BRAND
    growth_scores = {
        "revenue": rev_growth,
        "profit": profit_growth,
        "cups": cup_growth,
        "margin": margin_growth,
    }
    highest_growth = max(growth_scores, key=growth_scores.get)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card(
            "Revenue",
            rupiah(revenue),
            rev_delta,
            rev_color,
            "R",
            BRAND,
            "vs Last Year",
            sparkline_svg(monthly_kpi["revenue"], BRAND),
            highest_growth == "revenue",
        )
    with k2:
        kpi_card(
            "Gross Profit",
            rupiah(profit),
            profit_delta,
            profit_color,
            "P",
            BLUE,
            "vs Last Year",
            sparkline_svg(monthly_kpi["profit"], BLUE),
            highest_growth == "profit",
        )
    with k3:
        kpi_card(
            "Cups Sold",
            number(cups),
            cup_delta,
            cup_color,
            "C",
            "#22C55E",
            "vs Last Year",
            sparkline_svg(monthly_kpi["cups"], BRAND),
            highest_growth == "cups",
        )
    with k4:
        kpi_card(
            "Profit Margin",
            pct(margin),
            margin_delta,
            margin_color,
            "%",
            ORANGE,
            "vs Last Year",
            sparkline_svg(monthly_kpi["margin"], ORANGE),
            highest_growth == "margin",
        )

    st.markdown("<div style='height:0.12rem'></div>", unsafe_allow_html=True)

    monthly = (
        df.groupby("month", as_index=False)
        .agg(revenue=("total_revenue", "sum"), profit=("gross_profit", "sum"))
        .sort_values("month")
    )
    peak = monthly.loc[monthly["revenue"].idxmax()]
    latest = monthly.iloc[-1]
    previous = monthly.iloc[-2] if len(monthly) > 1 else monthly.iloc[-1]
    latest_growth, _ = growth(latest["revenue"], previous["revenue"])

    channel = pd.DataFrame(
        {
            "Channel": ["Dine in", "Delivery", "Takeaway"],
            "Revenue": [
                (df["total_revenue"] * df["dine_in_percent"] / 100).sum(),
                (df["total_revenue"] * df["delivery_percent"] / 100).sum(),
                (df["total_revenue"] * df["takeaway_percent"] / 100).sum(),
            ],
            "Gross Profit": [
                (df["gross_profit"] * df["dine_in_percent"] / 100).sum(),
                (df["gross_profit"] * df["delivery_percent"] / 100).sum(),
                (df["gross_profit"] * df["takeaway_percent"] / 100).sum(),
            ],
        }
    ).sort_values("Revenue", ascending=True)
    top_channel = channel.sort_values("Revenue", ascending=False).iloc[0]

    chart_left, chart_right = st.columns([2.15, 1])
    with chart_left:
        monthly["revenue_growth"] = monthly["revenue"].pct_change().fillna(0) * 100
        avg_revenue = monthly["revenue"].mean()
        target_revenue = avg_revenue * 1.15
        promo_month = (
            df[df["promo_type"] != "Tanpa promo"]
            .groupby("month", as_index=False)
            .agg(promo_revenue=("total_revenue", "sum"))
            .sort_values("promo_revenue", ascending=False)
        )
        milestone_month = promo_month.iloc[0]["month"] if not promo_month.empty else peak["month"]
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=monthly["month"],
                y=monthly["revenue"],
                name="Revenue",
                mode="lines",
                fill="tozeroy",
                line=dict(color=BRAND, width=3, shape="spline"),
                fillcolor="rgba(19, 185, 129, 0.12)",
                hovertemplate="<b>%{x|%b %Y}</b><br>Revenue: Rp %{y:,.0f}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=monthly["month"],
                y=monthly["profit"],
                name="Gross Profit",
                mode="lines",
                line=dict(color=BLUE, width=2.5, shape="spline"),
                hovertemplate="%{x|%b %Y}<br>Profit: Rp %{y:,.0f}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=monthly["month"],
                y=monthly["revenue_growth"],
                name="Revenue Growth",
                mode="lines+markers",
                line=dict(color=ORANGE, width=2, dash="dot"),
                marker=dict(size=5),
                hovertemplate="%{x|%b %Y}<br>Growth: %{y:.1f}%<extra></extra>",
            ),
            secondary_y=True,
        )
        fig = add_chart_title(
            fig,
            "Performance Overview",
            f"Revenue trend {latest_growth}; growth line highlights significant monthly movement.",
        )
        fig.add_hline(y=avg_revenue, line_dash="dash", line_color="#94A3B8", annotation_text="Avg Revenue", annotation_position="top left")
        fig.add_hline(y=target_revenue, line_dash="dot", line_color=ORANGE, annotation_text="Target", annotation_position="top left")
        fig.add_vline(x=milestone_month, line_width=1, line_dash="dot", line_color="#64748B", annotation_text="Campaign peak", annotation_position="top")
        fig.update_yaxes(title_text=None, secondary_y=False)
        fig.update_yaxes(title_text="Growth %", secondary_y=True, showgrid=False, tickfont=dict(size=9))
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig_style(fig, 292, True, top_margin=72), use_container_width=True, config={"displayModeBar": False})

    with chart_right:
        channel_desc = channel.sort_values("Revenue", ascending=False).copy()
        channel_desc["Contribution"] = channel_desc["Revenue"] / channel_desc["Revenue"].sum()
        channel_display = channel_desc.sort_values("Revenue", ascending=True)
        channel_display["Revenue Label"] = channel_display.apply(lambda row: f"{rupiah(row['Revenue'])} • {pct(row['Contribution'])}", axis=1)
        channel_display["Profit Label"] = channel_display["Gross Profit"].map(rupiah)
        fig_channel = go.Figure()
        fig_channel.add_trace(
            go.Bar(
                y=channel_display["Channel"],
                x=channel_display["Revenue"],
                orientation="h",
                name="Revenue",
                marker_color=BRAND,
                text=channel_display["Revenue Label"],
                textposition="outside",
                hovertemplate="%{y}<br>Revenue: Rp %{x:,.0f}<extra></extra>",
            )
        )
        fig_channel.add_trace(
            go.Bar(
                y=channel_display["Channel"],
                x=channel_display["Gross Profit"],
                orientation="h",
                name="Gross Profit",
                marker_color=BLUE,
                text=channel_display["Profit Label"],
                textposition="outside",
                hovertemplate="%{y}<br>Gross Profit: Rp %{x:,.0f}<extra></extra>",
            )
        )
        fig_channel = add_chart_title(
            fig_channel,
            "Revenue & Profit by Channel",
            f"{top_channel['Channel']} contributes the highest channel revenue.",
        )
        fig_channel.update_layout(barmode="group")
        st.plotly_chart(fig_style(fig_channel, 292, top_margin=72), use_container_width=True, config={"displayModeBar": False})

    branch = (
        df.groupby(["branch_name", "branch_city"], as_index=False)
        .agg(revenue=("total_revenue", "sum"), profit=("gross_profit", "sum"), satisfaction=("customer_satisfaction", "mean"))
        .sort_values("revenue", ascending=False)
    )
    latest_month = df["month"].max()
    previous_month = latest_month - pd.DateOffset(months=1)
    current_branch = (
        df[df["month"] == latest_month]
        .groupby("branch_name", as_index=False)
        .agg(current_revenue=("total_revenue", "sum"))
    )
    previous_branch = (
        df[df["month"] == previous_month]
        .groupby("branch_name", as_index=False)
        .agg(previous_revenue=("total_revenue", "sum"))
    )
    branch = branch.merge(current_branch, on="branch_name", how="left").merge(previous_branch, on="branch_name", how="left")
    branch[["current_revenue", "previous_revenue"]] = branch[["current_revenue", "previous_revenue"]].fillna(0)
    branch["growth"] = branch.apply(lambda row: growth_value(row["current_revenue"], row["previous_revenue"]), axis=1)

    category = (
        df.groupby("top_selling_category", as_index=False)
        .agg(cups=("total_cups_sold", "sum"), revenue=("total_revenue", "sum"), profit=("gross_profit", "sum"))
        .sort_values("profit", ascending=False)
    )
    category_melt = category.melt(
        id_vars="top_selling_category",
        value_vars=["revenue", "profit"],
        var_name="Metric",
        value_name="Value",
    )
    category_melt["Metric"] = category_melt["Metric"].map({"revenue": "Revenue", "profit": "Gross Profit"})

    promo_active_df = df[df["promo_type"] != "Tanpa promo"].copy()
    promo_active_df["promo_cost_est"] = promo_active_df["total_revenue"] * 0.08
    promo_active_df["promo_roi"] = (promo_active_df["gross_profit"] - promo_active_df["promo_cost_est"]) / promo_active_df["promo_cost_est"].where(
        promo_active_df["promo_cost_est"] != 0
    )
    promo = (
        promo_active_df.groupby("promo_type", as_index=False)
        .agg(revenue=("total_revenue", "sum"), gross_profit=("gross_profit", "sum"), promo_cost=("promo_cost_est", "sum"))
    )
    promo["roi"] = (promo["gross_profit"] - promo["promo_cost"]) / promo["promo_cost"].where(promo["promo_cost"] != 0)
    promo = promo.sort_values("roi", ascending=False)

    best_branch = branch.sort_values("revenue", ascending=False).iloc[0]
    best_category = category.sort_values("profit", ascending=False).iloc[0]
    best_promo_name = promo.iloc[0]["promo_type"] if not promo.empty else "Tidak ada promo aktif"
    insights = [
        f"Revenue moved {latest_growth} in the latest month.",
        f"{peak['month']:%b %Y} is the highest revenue month.",
        f"{top_channel['Channel']} contributes the highest channel revenue.",
        f"{best_promo_name} has the strongest estimated ROI.",
        f"{best_category['top_selling_category']} generates the highest gross profit.",
        f"{best_branch['branch_name']} is the top-performing branch.",
    ]
    insight_items = "".join(f"<div class='insight-item'>✓ {item}</div>" for item in insights)
    st.markdown(
        f"""
        <div class="insights-card">
            <div class="insights-title">Business Insights</div>
            <div class="insights-grid">{insight_items}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    bottom_left, bottom_mid, bottom_right = st.columns([1, 1, 1])
    with bottom_left:
        branch_top = branch.head(5).sort_values("revenue", ascending=True)
        branch_top["growth_label"] = branch_top["growth"].map(lambda value: f"{value * 100:+.1f}%")
        branch_top["bar_label"] = branch_top.apply(lambda row: f"{rupiah(row['revenue'])}  {row['growth_label']}", axis=1)
        branch_top["bar_color"] = branch_top["growth"].map(lambda value: RED if value < 0 else BRAND)
        fig_branch = px.bar(
            branch_top,
            x="revenue",
            y="branch_name",
            orientation="h",
            text="bar_label",
            color_discrete_sequence=[BRAND],
            hover_data={"branch_city": True, "revenue": ":,.0f", "growth_label": True, "branch_name": False, "growth": False},
        )
        fig_branch.update_traces(marker_color=branch_top["bar_color"], textposition="outside", cliponaxis=False)
        fig_branch = add_chart_title(
            fig_branch,
            "Top Branch Revenue & Growth",
            f"{best_branch['branch_name']} leads; red only flags negative growth.",
        )
        st.plotly_chart(fig_style(fig_branch, 202), use_container_width=True, config={"displayModeBar": False})
    with bottom_mid:
        category_chart = category_melt[category_melt["top_selling_category"].isin(category.head(5)["top_selling_category"])]
        order = category.head(5).sort_values("profit", ascending=True)["top_selling_category"]
        category_chart["top_selling_category"] = pd.Categorical(category_chart["top_selling_category"], categories=order, ordered=True)
        category_chart = category_chart.sort_values("top_selling_category")
        revenue_category = category_chart[category_chart["Metric"] == "Revenue"]
        profit_category = category_chart[category_chart["Metric"] == "Gross Profit"]
        highlight_lines = [ORANGE if category_name == best_category["top_selling_category"] else "rgba(0,0,0,0)" for category_name in profit_category["top_selling_category"]]
        fig_category = go.Figure()
        fig_category.add_trace(
            go.Bar(
                y=revenue_category["top_selling_category"],
                x=revenue_category["Value"],
                orientation="h",
                name="Revenue",
                marker_color=BLUE,
                text=revenue_category["Value"].map(rupiah),
                textposition="outside",
                hovertemplate="%{y}<br>Revenue: Rp %{x:,.0f}<extra></extra>",
            )
        )
        fig_category.add_trace(
            go.Bar(
                y=profit_category["top_selling_category"],
                x=profit_category["Value"],
                orientation="h",
                name="Gross Profit",
                marker_color=BRAND,
                marker_line_color=highlight_lines,
                marker_line_width=[3 if color == ORANGE else 0 for color in highlight_lines],
                text=profit_category["Value"].map(rupiah),
                textposition="outside",
                hovertemplate="%{y}<br>Gross Profit: Rp %{x:,.0f}<extra></extra>",
            )
        )
        fig_category = add_chart_title(
            fig_category,
            "Top Category by Revenue & Profit",
            f"{best_category['top_selling_category']} delivers the highest gross profit.",
        )
        fig_category.update_layout(barmode="group")
        st.plotly_chart(fig_style(fig_category, 202), use_container_width=True, config={"displayModeBar": False})
    with bottom_right:
        promo_chart = promo.head(5).sort_values("roi", ascending=False)
        if promo_chart.empty:
            promo_chart = pd.DataFrame({"promo_type": ["Tidak ada promo aktif"], "roi": [0], "revenue": [0], "promo_cost": [0], "gross_profit": [0]})
            best_promo = promo_chart.iloc[0]
        else:
            best_promo = promo.sort_values("roi", ascending=False).iloc[0]
        promo_chart["roi_pct"] = promo_chart["roi"] * 100
        fig_promo = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=["Promo", "ROI", "Revenue", "Cost", "Profit"],
                        fill_color="#F8FAFC",
                        align="left",
                        font=dict(color=DARK, size=11),
                        line_color="#E2E8F0",
                    ),
                    cells=dict(
                        values=[
                            promo_chart["promo_type"],
                            promo_chart["roi_pct"].map(lambda value: f"{value:.1f}%"),
                            promo_chart["revenue"].map(rupiah),
                            promo_chart["promo_cost"].map(rupiah),
                            promo_chart["gross_profit"].map(rupiah),
                        ],
                        fill_color="#FFFFFF",
                        align="left",
                        font=dict(color="#334155", size=10),
                        height=25,
                        line_color="#E2E8F0",
                    ),
                )
            ]
        )
        fig_promo = add_chart_title(
            fig_promo,
            "Promo ROI",
            f"{best_promo['promo_type']} has the strongest estimated promo ROI.",
        )
        st.plotly_chart(fig_style(fig_promo, 202), use_container_width=True, config={"displayModeBar": False})


def main() -> None:
    apply_style()
    df = load_data(DATA_PATH)

    st.markdown(
        """
        <div class="top-nav">
            <div class="brand-wrap">
                <div class="brand-dot">KS</div>
                <div class="brand-name">MarketPro</div>
                <div class="nav-link">Campaign Manager</div>
                <div class="nav-link active">Analytics</div>
                <div class="nav-link">Templates</div>
                <div class="nav-link">Automation</div>
                <div class="nav-link">Settings</div>
            </div>
            <div class="avatar">JD</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filtered = render_title_and_filters(df)
    build_dashboard(filtered)


if __name__ == "__main__":
    main()
