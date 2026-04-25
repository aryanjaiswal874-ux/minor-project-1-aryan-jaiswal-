import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Bank Transaction Analysis", page_icon="🏦", layout="wide")

# ─────────────────────────── CSS ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Background */
.stApp { background: #f5f7fa; }
[data-testid="stSidebar"] { background: #1e293b !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stMarkdown p { color: #94a3b8 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: white;
    border: none;
    border-radius: 12px;
    padding: 18px 20px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.05);
    border-left: 4px solid #3b82f6;
}
div[data-testid="stMetricValue"] {
    color: #1e293b !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}
div[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
div[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* Section headers */
h2 { color: #1e293b !important; font-weight: 700 !important; }
h3 { color: #334155 !important; font-weight: 600 !important; }

/* Upload area */
[data-testid="stFileUploader"] {
    background: white;
    border-radius: 12px;
    padding: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.07); }

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 28px !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stDownloadButton"] > button:hover { opacity: 0.9 !important; }

/* Tabs */
button[data-baseweb="tab"] { font-weight: 600 !important; font-size: 0.9rem !important; }

/* Divider */
hr { border-color: #e2e8f0 !important; margin: 1.5rem 0 !important; }

/* Success / warning / info */
[data-testid="stAlert"] { border-radius: 10px !important; font-size: 0.88rem !important; }

/* Footer */
.footer-text { text-align:center; color:#94a3b8; font-size:0.78rem; padding:12px 0; }

/* Sidebar multiselect */
[data-baseweb="tag"] { background: #3b82f6 !important; border-radius: 6px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────── PLOT THEME ───────────────────────
COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"]

def base_layout(**kwargs):
    d = dict(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter", color="#334155", size=12),
        margin=dict(l=16, r=16, t=36, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
        xaxis=dict(showgrid=False, linecolor="#e2e8f0", tickcolor="#e2e8f0"),
        yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickcolor="#e2e8f0",
                   rangemode="tozero"),
    )
    d.update(kwargs)
    return d

# ──────────────────────── HEADER ──────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1e293b 0%,#1e3a5f 100%);
            border-radius:16px;padding:28px 32px;margin-bottom:24px;">
  <h1 style="color:white;margin:0;font-size:1.8rem;font-weight:700;">
    🏦 Bank Transaction Analysis
  </h1>
  <p style="color:#94a3b8;margin:6px 0 0 0;font-size:0.9rem;">
    Interactive dashboard • Anomaly detection • Smart insights
  </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────── FILE UPLOAD ──────────────────────
uploaded_file = st.file_uploader("📂 Upload your bank CSV file", type=["csv"])

if uploaded_file is None:
    c1, c2, c3 = st.columns(3)
    c1.info("**Required columns**\nTransactionID, Date, Amount, Type")
    c2.info("**Supported date formats**\nYYYY-MM-DD · DD/MM/YYYY · DD-MM-YYYY")
    c3.info("**Tip**\nExport CSV directly from your bank's portal")
    st.stop()

# ──────────────────────── LOAD DATA ───────────────────────
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
df["Type"] = df["Type"].astype(str).str.strip()

df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
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

st.success(f"✅ Loaded **{len(df):,}** transactions  |  {df['Date'].min().strftime('%d %b %Y')} → {df['Date'].max().strftime('%d %b %Y')}")

# ──────────────────────── SIDEBAR ─────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Filters")
    st.markdown("---")

    date_min = df["Date"].min().date()
    date_max = df["Date"].max().date()
    start_date = st.date_input("From", date_min, min_value=date_min, max_value=date_max)
    end_date   = st.date_input("To",   date_max, min_value=date_min, max_value=date_max)

    if start_date > end_date:
        st.error("Start date must be ≤ End date")
        st.stop()

    types = sorted(df["Type"].dropna().unique().tolist())
    selected_types = st.multiselect("Transaction Type", options=types, default=types)
    if not selected_types:
        st.warning("Select at least one type.")
        st.stop()

    st.markdown("---")
    st.markdown("**Anomaly Sensitivity**")
    z_thresh = st.slider("Std deviations (σ)", 1.0, 4.0, 2.0, 0.5)
    st.markdown("---")
    st.markdown("<p style='font-size:0.75rem;color:#64748b;'>CSE Mini Project · 2024</p>", unsafe_allow_html=True)

# ─────────────────────── FILTER ───────────────────────────
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
filtered_df["Week"]      = filtered_df["Date"].dt.to_period("W").astype(str)

# ─────────────────────── STATS ────────────────────────────
total_amt = filtered_df["Amount"].sum()
mean_amt  = filtered_df["Amount"].mean()
max_amt   = filtered_df["Amount"].max()
min_amt   = filtered_df["Amount"].min()
txn_count = len(filtered_df)
std_amt   = filtered_df["Amount"].std()
std_amt   = 0.0 if pd.isna(std_amt) else std_amt

tl = filtered_df["Type"].str.lower()
credit_total = filtered_df[tl.str.contains("credit", na=False)]["Amount"].sum()
debit_total  = filtered_df[tl.str.contains("debit",  na=False)]["Amount"].sum()
net          = credit_total - debit_total

# ─────────────────────── METRICS ROW ──────────────────────
st.markdown("### 📊 Key Metrics")
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("💰 Total",    f"₹{total_amt:,.0f}")
m2.metric("📈 Average",  f"₹{mean_amt:,.0f}")
m3.metric("🔺 Highest",  f"₹{max_amt:,.0f}")
m4.metric("🔻 Lowest",   f"₹{min_amt:,.0f}")
m5.metric("🟢 Credit",   f"₹{credit_total:,.0f}")
m6.metric("🔴 Debit",    f"₹{debit_total:,.0f}")

st.markdown("---")

# ─────────────────────── TABS ─────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🍩 Breakdown", "🚨 Anomalies", "🗃️ Data"])

# ════════════════════ TAB 1 : TRENDS ════════════════════
with tab1:

    # ── Daily trend (area + line) ──
    st.markdown("#### Daily Transaction Trend")
    daily = (
        filtered_df.groupby("Date_only")["Amount"]
        .sum().reset_index()
        .rename(columns={"Date_only": "Date"})
        .sort_values("Date")
    )
    daily["MA7"] = daily["Amount"].rolling(7, min_periods=1).mean()

    if len(daily) < 2:
        fig_daily = px.bar(daily, x="Date", y="Amount",
                           color_discrete_sequence=[COLORS[0]])
    else:
        fig_daily = go.Figure()
        fig_daily.add_trace(go.Scatter(
            x=daily["Date"], y=daily["Amount"],
            fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
            line=dict(color=COLORS[0], width=2),
            mode="lines", name="Daily Total",
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>"
        ))
        fig_daily.add_trace(go.Scatter(
            x=daily["Date"], y=daily["MA7"],
            line=dict(color="#f59e0b", width=2, dash="dot"),
            mode="lines", name="7-day Avg",
            hovertemplate="7-day avg: ₹%{y:,.0f}<extra></extra>"
        ))

    fig_daily.update_layout(**base_layout(height=320,
        legend=dict(orientation="h", y=1.08, x=0)))
    fig_daily.update_yaxes(tickprefix="₹", tickformat=",")
    st.plotly_chart(fig_daily, use_container_width=True)

    # ── Monthly grouped bar (Credit vs Debit) ──
    st.markdown("#### Monthly Credit vs Debit")
    monthly_type = (
        filtered_df.groupby(["Month", "Type"])["Amount"]
        .sum().reset_index().sort_values("Month")
    )
    fig_mb = px.bar(
        monthly_type, x="Month", y="Amount", color="Type",
        barmode="group",
        color_discrete_sequence=COLORS,
        text=monthly_type["Amount"].apply(lambda x: f"₹{x/1000:.1f}k"),
    )
    fig_mb.update_traces(textposition="outside", textfont_size=10)
    fig_mb.update_layout(**base_layout(height=340,
        bargap=0.25, bargroupgap=0.08,
        legend=dict(orientation="h", y=1.08, x=0)))
    fig_mb.update_yaxes(tickprefix="₹", tickformat=",")
    st.plotly_chart(fig_mb, use_container_width=True)

    # ── Monthly summary table ──
    st.markdown("#### Monthly Summary Table")
    mtable = (
        filtered_df.groupby("Month").agg(
            Total=("Amount","sum"), Average=("Amount","mean"),
            Max=("Amount","max"), Transactions=("Amount","count")
        ).reset_index().sort_values("Month")
    )
    for col in ["Total","Average","Max"]:
        mtable[col] = mtable[col].round(2)
    mtable.columns = ["Month","Total (₹)","Avg (₹)","Max (₹)","Txns"]
    st.dataframe(mtable.reset_index(drop=True), use_container_width=True, hide_index=True)

# ════════════════════ TAB 2 : BREAKDOWN ════════════════════
with tab2:
    col_l, col_r = st.columns(2)

    # ── Donut chart ──
    with col_l:
        st.markdown("#### Share by Type")
        type_grp = filtered_df.groupby("Type")["Amount"].sum().reset_index()
        type_grp = type_grp[type_grp["Amount"] > 0]

        if len(type_grp) == 1:
            fig_pie = px.bar(type_grp, x="Type", y="Amount",
                             color_discrete_sequence=[COLORS[0]])
        else:
            fig_pie = go.Figure(go.Pie(
                labels=type_grp["Type"],
                values=type_grp["Amount"],
                hole=0.52,
                marker=dict(colors=COLORS,
                            line=dict(color="white", width=3)),
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>"
            ))
            fig_pie.add_annotation(
                text=f"<b>₹{total_amt/1e5:.1f}L</b><br><span style='font-size:11px'>Total</span>",
                x=0.5, y=0.5, showarrow=False, font=dict(size=15, color="#1e293b")
            )
        fig_pie.update_layout(**base_layout(height=320,
            showlegend=True,
            legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center")))
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Horizontal bar by type ──
    with col_r:
        st.markdown("#### Amount by Type")
        type_sorted = type_grp.sort_values("Amount", ascending=True)
        fig_hbar = go.Figure(go.Bar(
            x=type_sorted["Amount"],
            y=type_sorted["Type"],
            orientation="h",
            marker=dict(
                color=COLORS[:len(type_sorted)],
                line=dict(color="white", width=1)
            ),
            text=type_sorted["Amount"].apply(lambda x: f"₹{x:,.0f}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>"
        ))
        fig_hbar.update_layout(**base_layout(height=320))
        fig_hbar.update_xaxes(tickprefix="₹", tickformat=",")
        st.plotly_chart(fig_hbar, use_container_width=True)

    # ── Weekly heatmap-style bar ──
    st.markdown("#### Spending by Day of Week")
    filtered_df["DayOfWeek"] = filtered_df["Date"].dt.day_name()
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow = (
        filtered_df.groupby("DayOfWeek")["Amount"]
        .sum().reindex(dow_order, fill_value=0).reset_index()
    )
    dow.columns = ["Day","Amount"]
    fig_dow = px.bar(
        dow, x="Day", y="Amount",
        color="Amount", color_continuous_scale=["#dbeafe","#1d4ed8"],
        text=dow["Amount"].apply(lambda x: f"₹{x/1000:.1f}k")
    )
    fig_dow.update_traces(textposition="outside", textfont_size=10)
    fig_dow.update_layout(**base_layout(height=300,
        coloraxis_showscale=False))
    fig_dow.update_yaxes(tickprefix="₹", tickformat=",")
    st.plotly_chart(fig_dow, use_container_width=True)

    # ── Top 10 transactions ──
    st.markdown("#### Top 10 Largest Transactions")
    top10 = (
        filtered_df.nlargest(10, "Amount")
        .drop(columns=["Month","Date_only","Week","DayOfWeek"], errors="ignore")
        .reset_index(drop=True)
    )
    top10.index += 1
    st.dataframe(top10, use_container_width=True)

# ════════════════════ TAB 3 : ANOMALIES ════════════════════
with tab3:
    st.markdown("#### Anomaly Detection")

    if std_amt == 0 or txn_count < 3:
        st.info("Not enough variation to detect anomalies.")
    else:
        threshold = mean_amt + z_thresh * std_amt

        col_info1, col_info2, col_info3 = st.columns(3)
        col_info1.metric("Mean",      f"₹{mean_amt:,.2f}")
        col_info2.metric("Std Dev",   f"₹{std_amt:,.2f}")
        col_info3.metric("Threshold (mean + "+str(z_thresh)+"σ)", f"₹{threshold:,.2f}")

        anomalies = filtered_df[filtered_df["Amount"] > threshold].copy()

        # ── Scatter: all txns + anomalies highlighted ──
        scatter_df = filtered_df.copy()
        scatter_df["Status"] = scatter_df["Amount"].apply(
            lambda x: "Anomaly 🔴" if x > threshold else "Normal 🔵"
        )
        fig_sc = px.scatter(
            scatter_df, x="Date_only", y="Amount",
            color="Status",
            color_discrete_map={"Anomaly 🔴": "#ef4444", "Normal 🔵": "#3b82f6"},
            opacity=0.75, size_max=12,
            hover_data={"Type": True, "Date_only": False},
            labels={"Date_only": "Date", "Amount": "Amount (₹)"}
        )
        fig_sc.update_traces(marker=dict(size=8))
        fig_sc.add_hline(
            y=threshold, line_dash="dash", line_color="#f59e0b", line_width=2,
            annotation_text=f"  Threshold ₹{threshold:,.0f}",
            annotation_font=dict(color="#92400e", size=12)
        )
        fig_sc.update_layout(**base_layout(height=360,
            legend=dict(orientation="h", y=1.08, x=0)))
        fig_sc.update_xaxes(title="Date")
        fig_sc.update_yaxes(tickprefix="₹", tickformat=",")
        st.plotly_chart(fig_sc, use_container_width=True)

        # ── Amount distribution histogram ──
        st.markdown("#### Amount Distribution")
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=filtered_df["Amount"], nbinsx=40,
            marker=dict(color="#3b82f6", line=dict(color="white", width=0.5)),
            name="Transactions",
            hovertemplate="₹%{x}<br>Count: %{y}<extra></extra>"
        ))
        fig_hist.add_vline(
            x=threshold, line_dash="dash", line_color="#ef4444", line_width=2,
            annotation_text=f" Threshold",
            annotation_font=dict(color="#ef4444", size=11)
        )
        fig_hist.add_vline(
            x=mean_amt, line_dash="dot", line_color="#10b981", line_width=2,
            annotation_text=f" Mean",
            annotation_font=dict(color="#065f46", size=11)
        )
        fig_hist.update_layout(**base_layout(height=300))
        fig_hist.update_xaxes(tickprefix="₹", tickformat=",", title="Amount")
        fig_hist.update_yaxes(title="Count")
        st.plotly_chart(fig_hist, use_container_width=True)

        # ── Anomaly table ──
        if not anomalies.empty:
            st.warning(f"⚠️ {len(anomalies)} unusual transaction(s) found above ₹{threshold:,.0f}")
            show_anom = anomalies.drop(
                columns=["Month","Date_only","Week","DayOfWeek","Status"], errors="ignore"
            ).sort_values("Amount", ascending=False).reset_index(drop=True)
            show_anom.index += 1
            st.dataframe(show_anom, use_container_width=True)
        else:
            st.success("✅ No unusual transactions at this sensitivity level.")

# ════════════════════ TAB 4 : DATA ════════════════════
with tab4:
    st.markdown(f"#### All Transactions &nbsp; `{txn_count:,} rows`")
    show_df = filtered_df.drop(
        columns=["Month","Date_only","Week","DayOfWeek"], errors="ignore"
    ).reset_index(drop=True)
    st.dataframe(show_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    dl_df = filtered_df.drop(
        columns=["Month","Date_only","Week","DayOfWeek"], errors="ignore"
    )
    st.download_button(
        "⬇️ Download Filtered CSV",
        data=dl_df.to_csv(index=False),
        file_name="filtered_transactions.csv",
        mime="text/csv"
    )

# ──────────────────────── FOOTER ──────────────────────────
st.markdown("---")
st.markdown(
    "<div class='footer-text'>Built with Streamlit + Plotly &nbsp;·&nbsp; "
    "CSE 3rd Sem Mini Project &nbsp;·&nbsp; 2024</div>",
    unsafe_allow_html=True
)
