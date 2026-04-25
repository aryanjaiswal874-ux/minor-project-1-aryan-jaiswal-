import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="FinLens · Bank Analysis",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════
#  CSS  — editorial dark-cream split theme
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #f7f4ef;
}
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1280px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f0f0f !important;
    border-right: 1px solid #222 !important;
}
[data-testid="stSidebar"] * { color: #c8c0b4 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f0ebe3 !important; }
[data-testid="stSidebar"] .stMarkdown hr { border-color: #2a2a2a !important; }
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] select { background: #1a1a1a !important; border-color: #333 !important; color: #e0d8cc !important; }
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: #c9a96e !important;
    border-radius: 4px !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] div[data-baseweb="slider"] div {
    background: #c9a96e !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #0f0f0f;
    border: none;
    border-radius: 10px;
    padding: 20px 22px !important;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: #c9a96e;
}
div[data-testid="stMetricValue"] {
    font-family: 'DM Serif Display', serif !important;
    color: #f0ebe3 !important;
    font-size: 1.65rem !important;
    font-weight: 400 !important;
    letter-spacing: -0.5px;
}
div[data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: #7a7060 !important;
    font-size: 0.65rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}
div[data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
}

/* ── Section titles (markdown h4) ── */
h4 { color: #1a1a1a !important; font-family: 'DM Serif Display', serif !important;
     font-weight: 400 !important; font-size: 1.25rem !important; margin-top: 0.5rem !important; }
h3 { color: #1a1a1a !important; font-family: 'DM Serif Display', serif !important;
     font-weight: 400 !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 2px solid #e0d8cc !important;
    gap: 0 !important;
}
[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #9a8f82 !important;
    padding: 10px 20px !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #0f0f0f !important;
    border-bottom: 2px solid #c9a96e !important;
    background: transparent !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 8px !important;
    border: 1px solid #e0d8cc !important;
    overflow: hidden !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: #0f0f0f !important;
    color: #f0ebe3 !important;
    border: 1px solid #0f0f0f !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px;
    padding: 10px 28px !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #c9a96e !important;
    border-color: #c9a96e !important;
    color: #0f0f0f !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: white;
    border: 1.5px dashed #c8bfb2;
    border-radius: 10px;
    padding: 6px 12px;
}

/* ── Divider ── */
hr { border-color: #e0d8cc !important; }

/* ── Chart wrapper card ── */
.chart-card {
    background: white;
    border-radius: 10px;
    border: 1px solid #e8e2d9;
    padding: 20px 20px 8px 20px;
    margin-bottom: 16px;
}
.chart-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #9a8f82;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
}
.chart-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.1rem;
    color: #1a1a1a;
    margin-bottom: 12px;
}

/* ── Insight pill ── */
.insight-pill {
    display: inline-block;
    background: #0f0f0f;
    color: #c9a96e;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    padding: 5px 14px;
    border-radius: 100px;
    margin: 3px;
    letter-spacing: 0.3px;
}

/* ── Success banner ── */
.loaded-banner {
    background: #0f0f0f;
    border-radius: 8px;
    padding: 10px 18px;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}
.loaded-banner span { color: #c8c0b4; font-size: 0.83rem; font-family: 'JetBrains Mono', monospace; }
.loaded-banner .dot { width: 8px; height: 8px; background: #4ade80; border-radius: 50%; flex-shrink: 0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  PLOTLY THEME
# ══════════════════════════════════════════════════════
PAL   = ["#c9a96e", "#4a90a4", "#e07b54", "#6aaa7e", "#9b72aa", "#5b8fd4"]
GOLD  = "#c9a96e"
DARK  = "#0f0f0f"
CREAM = "#f7f4ef"
CARD_BG = "white"

def chart_layout(h=340, **kw):
    base = dict(
        height=h,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(family="DM Sans", color="#4a4540", size=12),
        margin=dict(l=8, r=8, t=12, b=8),
        xaxis=dict(
            showgrid=False, zeroline=False,
            linecolor="#e8e2d9", tickcolor="#e8e2d9",
            tickfont=dict(size=11, color="#9a8f82")
        ),
        yaxis=dict(
            gridcolor="#f0ebe3", zeroline=False,
            linecolor="#e8e2d9", tickcolor="#e8e2d9",
            rangemode="tozero",
            tickfont=dict(size=11, color="#9a8f82")
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color="#4a4540"),
            borderwidth=0
        ),
        hoverlabel=dict(
            bgcolor=DARK, font_color="#f0ebe3",
            font_family="DM Sans", font_size=12,
            bordercolor=DARK
        )
    )
    base.update(kw)
    return base

def card(label, title):
    st.markdown(f"""
    <div class="chart-card">
      <div class="chart-label">{label}</div>
      <div class="chart-title">{title}</div>
    """, unsafe_allow_html=True)

def card_end():
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════
st.markdown("""
<div style="display:flex;align-items:flex-end;justify-content:space-between;
            border-bottom:2px solid #0f0f0f;padding-bottom:16px;margin-bottom:24px;">
  <div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                color:#9a8f82;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">
      Financial Intelligence Dashboard
    </div>
    <h1 style="font-family:'DM Serif Display',serif;font-size:2.4rem;font-weight:400;
               color:#0f0f0f;margin:0;letter-spacing:-1px;line-height:1.1;">
      FinLens
    </h1>
  </div>
  <div style="text-align:right;">
    <div style="font-family:'DM Sans',sans-serif;font-size:0.8rem;color:#9a8f82;">
      Transaction Analysis · Anomaly Detection
    </div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#c9a96e;margin-top:2px;">
      CSE Mini Project · 2024
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  UPLOAD
# ══════════════════════════════════════════════════════
uploaded_file = st.file_uploader("Upload bank CSV  (TransactionID · Date · Amount · Type)", type=["csv"])

if uploaded_file is None:
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:12px;">
      <div style="background:white;border:1px solid #e8e2d9;border-radius:10px;padding:20px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#9a8f82;
                    text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">Required</div>
        <div style="font-size:0.9rem;color:#1a1a1a;">TransactionID, Date,<br>Amount, Type</div>
      </div>
      <div style="background:white;border:1px solid #e8e2d9;border-radius:10px;padding:20px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#9a8f82;
                    text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">Date formats</div>
        <div style="font-size:0.9rem;color:#1a1a1a;">YYYY-MM-DD<br>DD/MM/YYYY</div>
      </div>
      <div style="background:white;border:1px solid #e8e2d9;border-radius:10px;padding:20px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#9a8f82;
                    text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">Tip</div>
        <div style="font-size:0.9rem;color:#1a1a1a;">Export CSV directly<br>from your bank portal</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════
#  LOAD & CLEAN
# ══════════════════════════════════════════════════════
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Could not read file: {e}")
    st.stop()

required_cols = {"TransactionID", "Date", "Amount", "Type"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"Missing columns: {', '.join(missing)}")
    st.stop()

df.columns = df.columns.str.strip()
df["Type"]  = df["Type"].astype(str).str.strip()
df["Date"]  = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["Date"])

df["Amount"] = (
    df["Amount"].astype(str)
    .str.replace(r"[₹$,\s]", "", regex=True).str.strip()
)
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df = df.dropna(subset=["Amount"])
if (df["Amount"] < 0).any():
    df["Amount"] = df["Amount"].abs()

if df.empty:
    st.error("No valid data after cleaning.")
    st.stop()

date_range = f"{df['Date'].min().strftime('%d %b %Y')}  →  {df['Date'].max().strftime('%d %b %Y')}"
st.markdown(f"""
<div class="loaded-banner">
  <div class="dot"></div>
  <span>Loaded <b style="color:#f0ebe3">{len(df):,}</b> transactions &nbsp;·&nbsp; {date_range}</span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="font-family:'DM Serif Display',serif;font-size:1.4rem;
                color:#f0ebe3;margin-bottom:4px;">Filters</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                color:#7a7060;letter-spacing:1px;text-transform:uppercase;
                margin-bottom:16px;">Refine your view</div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    date_min = df["Date"].min().date()
    date_max = df["Date"].max().date()
    start_date = st.date_input("From", date_min, min_value=date_min, max_value=date_max)
    end_date   = st.date_input("To",   date_max, min_value=date_min, max_value=date_max)

    if start_date > end_date:
        st.error("Start must be ≤ End")
        st.stop()

    st.markdown("---")
    types = sorted(df["Type"].dropna().unique().tolist())
    selected_types = st.multiselect("Transaction Type", options=types, default=types)
    if not selected_types:
        st.warning("Select at least one type.")
        st.stop()

    st.markdown("---")
    st.markdown("<span style='font-family:JetBrains Mono,monospace;font-size:0.6rem;letter-spacing:1px;text-transform:uppercase;'>Anomaly Sensitivity</span>", unsafe_allow_html=True)
    z_thresh = st.slider("Std deviations (σ)", 1.0, 4.0, 2.0, 0.5,
                         label_visibility="collapsed")
    st.markdown(f"<span style='font-family:JetBrains Mono,monospace;font-size:0.7rem;color:#c9a96e;'>σ = {z_thresh}</span>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  FILTER
# ══════════════════════════════════════════════════════
filtered_df = df[
    (df["Date"].dt.date >= start_date) &
    (df["Date"].dt.date <= end_date) &
    (df["Type"].isin(selected_types))
].copy()

if filtered_df.empty:
    st.warning("No data matches your filters.")
    st.stop()

filtered_df["Month"]     = filtered_df["Date"].dt.to_period("M").astype(str)
filtered_df["Date_only"] = filtered_df["Date"].dt.date
filtered_df["DayOfWeek"] = filtered_df["Date"].dt.day_name()

# ══════════════════════════════════════════════════════
#  STATS
# ══════════════════════════════════════════════════════
total_amt = filtered_df["Amount"].sum()
mean_amt  = filtered_df["Amount"].mean()
max_amt   = filtered_df["Amount"].max()
min_amt   = filtered_df["Amount"].min()
txn_count = len(filtered_df)
std_amt   = filtered_df["Amount"].std()
std_amt   = 0.0 if (pd.isna(std_amt) or std_amt == 0) else std_amt

tl = filtered_df["Type"].str.lower()
credit_total = filtered_df[tl.str.contains("credit", na=False)]["Amount"].sum()
debit_total  = filtered_df[tl.str.contains("debit",  na=False)]["Amount"].sum()
net          = credit_total - debit_total

# ══════════════════════════════════════════════════════
#  METRIC ROW
# ══════════════════════════════════════════════════════
st.markdown("<div style='font-family:DM Serif Display,serif;font-size:1.3rem;color:#1a1a1a;margin-bottom:12px;'>Overview</div>", unsafe_allow_html=True)

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Total Volume",  f"₹{total_amt:,.0f}")
m2.metric("Avg per Txn",   f"₹{mean_amt:,.0f}")
m3.metric("Highest",       f"₹{max_amt:,.0f}")
m4.metric("Lowest",        f"₹{min_amt:,.0f}")
m5.metric("Credit In",     f"₹{credit_total:,.0f}")
m6.metric("Debit Out",     f"₹{debit_total:,.0f}")

# Net balance bar
net_pct = (credit_total / (credit_total + debit_total) * 100) if (credit_total + debit_total) > 0 else 50
net_color = "#4ade80" if net >= 0 else "#f87171"
net_label = f"₹{abs(net):,.0f} {'surplus' if net >= 0 else 'deficit'}"
st.markdown(f"""
<div style="background:white;border:1px solid #e8e2d9;border-radius:10px;
            padding:14px 20px;margin:12px 0 20px 0;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                 color:#9a8f82;text-transform:uppercase;letter-spacing:1.5px;">Net Balance</span>
    <span style="font-family:'DM Serif Display',serif;font-size:1rem;color:{net_color};">{net_label}</span>
  </div>
  <div style="background:#f0ebe3;border-radius:4px;height:6px;overflow:hidden;">
    <div style="background:{net_color};height:100%;width:{net_pct:.1f}%;border-radius:4px;
                transition:width 0.4s;"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:5px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#4ade80;">Credit {net_pct:.1f}%</span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#f87171;">Debit {100-net_pct:.1f}%</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["  Trends  ", "  Breakdown  ", "  Anomalies  ", "  Data  "])

# ─────────────── TAB 1 : TRENDS ───────────────
with tab1:
    # Daily area chart
    daily = (
        filtered_df.groupby("Date_only")["Amount"]
        .sum().reset_index()
        .rename(columns={"Date_only": "Date"})
        .sort_values("Date")
    )
    daily["MA7"] = daily["Amount"].rolling(7, min_periods=1).mean()

    st.markdown("""<div class="chart-card"><div class="chart-label">Transaction Activity</div>
    <div class="chart-title">Daily spend with 7-day moving average</div>""", unsafe_allow_html=True)

    if len(daily) < 2:
        fig1 = px.bar(daily, x="Date", y="Amount", color_discrete_sequence=[GOLD])
    else:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=daily["Date"], y=daily["Amount"],
            fill="tozeroy",
            fillcolor="rgba(201,169,110,0.10)",
            line=dict(color=GOLD, width=2),
            mode="lines", name="Daily",
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>"
        ))
        fig1.add_trace(go.Scatter(
            x=daily["Date"], y=daily["MA7"],
            line=dict(color="#4a90a4", width=2, dash="dot"),
            mode="lines", name="7-day avg",
            hovertemplate="Avg: ₹%{y:,.0f}<extra></extra>"
        ))
    fig1.update_layout(**chart_layout(h=300,
        legend=dict(orientation="h", y=1.12, x=0, xanchor="left")))
    fig1.update_yaxes(tickprefix="₹", tickformat=",")
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Monthly grouped
    st.markdown("""<div class="chart-card"><div class="chart-label">Monthly View</div>
    <div class="chart-title">Credit vs Debit by month</div>""", unsafe_allow_html=True)

    monthly_type = (
        filtered_df.groupby(["Month", "Type"])["Amount"]
        .sum().reset_index().sort_values("Month")
    )
    fig_mb = px.bar(
        monthly_type, x="Month", y="Amount", color="Type",
        barmode="group",
        color_discrete_sequence=PAL,
        text=monthly_type["Amount"].apply(lambda x: f"₹{x/1000:.0f}k"),
    )
    fig_mb.update_traces(textposition="outside", textfont_size=9,
                         marker_line_width=0)
    fig_mb.update_layout(**chart_layout(h=300,
        bargap=0.28, bargroupgap=0.06,
        legend=dict(orientation="h", y=1.12, x=0)))
    fig_mb.update_yaxes(tickprefix="₹", tickformat=",")
    st.plotly_chart(fig_mb, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Monthly table
    st.markdown("""<div class="chart-card"><div class="chart-label">Monthly Summary</div>
    <div class="chart-title">Aggregated stats per month</div>""", unsafe_allow_html=True)
    mtable = (
        filtered_df.groupby("Month").agg(
            Total=("Amount","sum"), Average=("Amount","mean"),
            Max=("Amount","max"), Count=("Amount","count")
        ).reset_index().sort_values("Month")
    )
    for c in ["Total","Average","Max"]:
        mtable[c] = mtable[c].round(0).astype(int)
    mtable.columns = ["Month","Total (₹)","Avg (₹)","Max (₹)","Transactions"]
    st.dataframe(mtable.reset_index(drop=True), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────── TAB 2 : BREAKDOWN ───────────────
with tab2:
    type_grp = filtered_df.groupby("Type")["Amount"].sum().reset_index()
    type_grp = type_grp[type_grp["Amount"] > 0].sort_values("Amount", ascending=False)

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown("""<div class="chart-card"><div class="chart-label">Composition</div>
        <div class="chart-title">Share by transaction type</div>""", unsafe_allow_html=True)

        if len(type_grp) == 1:
            fig_pie = px.bar(type_grp, x="Type", y="Amount",
                             color_discrete_sequence=[GOLD])
        else:
            fig_pie = go.Figure(go.Pie(
                labels=type_grp["Type"], values=type_grp["Amount"],
                hole=0.58,
                marker=dict(colors=PAL, line=dict(color="white", width=3)),
                textinfo="label+percent",
                textfont=dict(size=11, family="DM Sans"),
                hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>"
            ))
            fig_pie.add_annotation(
                text=f"<b>₹{total_amt/1e5:.1f}L</b><br><span style='font-size:10px;color:#9a8f82'>total</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#1a1a1a", family="DM Serif Display")
            )
        fig_pie.update_layout(**chart_layout(h=300,
            showlegend=True,
            legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center")))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown("""<div class="chart-card"><div class="chart-label">Volume</div>
        <div class="chart-title">Amount by type (ranked)</div>""", unsafe_allow_html=True)

        type_sorted = type_grp.sort_values("Amount", ascending=True)
        bars = go.Figure(go.Bar(
            x=type_sorted["Amount"], y=type_sorted["Type"],
            orientation="h",
            marker=dict(color=PAL[:len(type_sorted)][::-1], line_width=0),
            text=type_sorted["Amount"].apply(lambda x: f"  ₹{x:,.0f}"),
            textposition="outside",
            textfont=dict(size=11, color="#4a4540"),
            hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>"
        ))
        bars.update_layout(**chart_layout(h=300))
        bars.update_xaxes(tickprefix="₹", tickformat=",", showgrid=True, gridcolor="#f0ebe3")
        bars.update_yaxes(showgrid=False)
        st.plotly_chart(bars, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Day of week
    st.markdown("""<div class="chart-card"><div class="chart-label">Behaviour</div>
    <div class="chart-title">Spending pattern by day of week</div>""", unsafe_allow_html=True)

    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow = (
        filtered_df.groupby("DayOfWeek")["Amount"]
        .sum().reindex(dow_order, fill_value=0).reset_index()
    )
    dow.columns = ["Day","Amount"]
    dow["pct"] = (dow["Amount"] / dow["Amount"].max() * 100).round(1)

    fig_dow = go.Figure()
    fig_dow.add_trace(go.Bar(
        x=dow["Day"], y=dow["Amount"],
        marker=dict(
            color=dow["Amount"],
            colorscale=[[0,"#f0ebe3"],[0.5,"#c9a96e"],[1,"#8b6914"]],
            line_width=0
        ),
        text=dow["Amount"].apply(lambda x: f"₹{x/1000:.1f}k"),
        textposition="outside",
        textfont=dict(size=10, color="#4a4540"),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>"
    ))
    fig_dow.update_layout(**chart_layout(h=280, coloraxis_showscale=False))
    fig_dow.update_yaxes(tickprefix="₹", tickformat=",")
    st.plotly_chart(fig_dow, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Top 10
    st.markdown("""<div class="chart-card"><div class="chart-label">Leaderboard</div>
    <div class="chart-title">Top 10 largest transactions</div>""", unsafe_allow_html=True)
    top10 = (
        filtered_df.nlargest(10, "Amount")
        .drop(columns=["Month","Date_only","DayOfWeek"], errors="ignore")
        .reset_index(drop=True)
    )
    top10.index += 1
    st.dataframe(top10, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────── TAB 3 : ANOMALIES ───────────────
with tab3:
    if std_amt == 0 or txn_count < 3:
        st.info("Not enough variation in data to detect anomalies.")
    else:
        threshold = mean_amt + z_thresh * std_amt
        anomalies = filtered_df[filtered_df["Amount"] > threshold]

        # Stat bar
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px;">
          <div style="background:#0f0f0f;border-radius:10px;padding:16px 18px;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#7a7060;
                        text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;">Mean</div>
            <div style="font-family:'DM Serif Display',serif;font-size:1.3rem;color:#f0ebe3;">₹{mean_amt:,.0f}</div>
          </div>
          <div style="background:#0f0f0f;border-radius:10px;padding:16px 18px;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#7a7060;
                        text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;">Std Dev</div>
            <div style="font-family:'DM Serif Display',serif;font-size:1.3rem;color:#f0ebe3;">₹{std_amt:,.0f}</div>
          </div>
          <div style="background:#0f0f0f;border-radius:10px;padding:16px 18px;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#7a7060;
                        text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;">Threshold ({z_thresh}σ)</div>
            <div style="font-family:'DM Serif Display',serif;font-size:1.3rem;color:#c9a96e;">₹{threshold:,.0f}</div>
          </div>
          <div style="background:{'#3d1515' if len(anomalies)>0 else '#0f2a1a'};border-radius:10px;padding:16px 18px;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#7a7060;
                        text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;">Flagged</div>
            <div style="font-family:'DM Serif Display',serif;font-size:1.3rem;color:{'#f87171' if len(anomalies)>0 else '#4ade80'};">
              {len(anomalies)} txn{'s' if len(anomalies)!=1 else ''}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Scatter
        st.markdown("""<div class="chart-card"><div class="chart-label">Detection</div>
        <div class="chart-title">All transactions — anomalies highlighted</div>""", unsafe_allow_html=True)

        scatter_df = filtered_df.copy()
        scatter_df["Flag"] = scatter_df["Amount"].apply(
            lambda x: "Anomaly" if x > threshold else "Normal"
        )
        fig_sc = go.Figure()
        normal_df = scatter_df[scatter_df["Flag"] == "Normal"]
        anom_df   = scatter_df[scatter_df["Flag"] == "Anomaly"]
        fig_sc.add_trace(go.Scatter(
            x=normal_df["Date_only"], y=normal_df["Amount"],
            mode="markers", name="Normal",
            marker=dict(color=GOLD, size=6, opacity=0.5, line_width=0),
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>"
        ))
        if not anom_df.empty:
            fig_sc.add_trace(go.Scatter(
                x=anom_df["Date_only"], y=anom_df["Amount"],
                mode="markers", name="Anomaly",
                marker=dict(color="#f87171", size=11, symbol="diamond",
                            line=dict(color="white", width=1.5)),
                hovertemplate="<b>ANOMALY</b><br>%{x}<br>₹%{y:,.0f}<extra></extra>"
            ))
        fig_sc.add_hline(
            y=threshold, line_dash="dash", line_color="#e07b54", line_width=1.5,
            annotation_text=f"  ₹{threshold:,.0f} threshold",
            annotation_font=dict(color="#e07b54", size=11, family="JetBrains Mono")
        )
        fig_sc.update_layout(**chart_layout(h=320,
            legend=dict(orientation="h", y=1.1, x=0)))
        fig_sc.update_yaxes(tickprefix="₹", tickformat=",")
        st.plotly_chart(fig_sc, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Histogram
        st.markdown("""<div class="chart-card"><div class="chart-label">Distribution</div>
        <div class="chart-title">Amount frequency with threshold line</div>""", unsafe_allow_html=True)

        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=filtered_df["Amount"], nbinsx=40,
            marker=dict(color=GOLD, opacity=0.75, line=dict(color="white", width=0.4)),
            name="Transactions",
            hovertemplate="₹%{x}<br>Count: %{y}<extra></extra>"
        ))
        fig_hist.add_vline(x=mean_amt, line_dash="dot", line_color="#4a90a4", line_width=2,
                           annotation_text=" Mean",
                           annotation_font=dict(color="#4a90a4", size=10, family="JetBrains Mono"))
        fig_hist.add_vline(x=threshold, line_dash="dash", line_color="#f87171", line_width=2,
                           annotation_text=" Threshold",
                           annotation_font=dict(color="#f87171", size=10, family="JetBrains Mono"))
        fig_hist.update_layout(**chart_layout(h=280))
        fig_hist.update_xaxes(tickprefix="₹", tickformat=",", title="Amount")
        fig_hist.update_yaxes(title="Count")
        st.plotly_chart(fig_hist, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Anomaly table
        if not anomalies.empty:
            st.markdown("""<div class="chart-card"><div class="chart-label">Flagged Records</div>
            <div class="chart-title">Transactions above threshold</div>""", unsafe_allow_html=True)
            show_anom = (
                anomalies.drop(columns=["Month","Date_only","DayOfWeek","Flag"], errors="ignore")
                .sort_values("Amount", ascending=False)
                .reset_index(drop=True)
            )
            show_anom.index += 1
            st.dataframe(show_anom, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.success("✅ No anomalies detected at this sensitivity level.")

# ─────────────── TAB 4 : DATA ───────────────
with tab4:
    st.markdown(f"""<div class="chart-card">
    <div class="chart-label">Raw Records</div>
    <div class="chart-title">All {txn_count:,} transactions</div>""", unsafe_allow_html=True)

    show_df = filtered_df.drop(
        columns=["Month","Date_only","DayOfWeek"], errors="ignore"
    ).reset_index(drop=True)
    st.dataframe(show_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    dl_df = filtered_df.drop(columns=["Month","Date_only","DayOfWeek"], errors="ignore")
    st.download_button(
        "⬇  Export filtered CSV",
        data=dl_df.to_csv(index=False),
        file_name="transactions_filtered.csv",
        mime="text/csv"
    )

# ══════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════
st.markdown("""
<div style="border-top:1px solid #e0d8cc;margin-top:32px;padding-top:14px;
            display:flex;justify-content:space-between;align-items:center;">
  <span style="font-family:'DM Serif Display',serif;font-size:1rem;color:#9a8f82;">FinLens</span>
  <span style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:#bbb0a4;letter-spacing:0.5px;">
    Streamlit · Plotly · Pandas &nbsp;·&nbsp; CSE 3rd Sem Mini Project 2024
  </span>
</div>
""", unsafe_allow_html=True)
