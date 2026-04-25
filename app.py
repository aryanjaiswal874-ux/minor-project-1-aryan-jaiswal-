import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Bank Transaction Dashboard",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  (student-ish: bold colors,
#  slightly over-enthusiastic, but clean)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* ── sidebar ── */
section[data-testid="stSidebar"] {
    background: #1a1a2e;
    color: white;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* ── metric cards ── */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
    border: 1px solid #e94560;
    border-radius: 12px;
    padding: 16px 20px;
    color: white !important;
}
div[data-testid="metric-container"] label,
div[data-testid="metric-container"] div {
    color: white !important;
}

/* ── section headers ── */
h2, h3 {
    color: #0f3460;
    border-bottom: 3px solid #e94560;
    padding-bottom: 4px;
}

/* ── dataframe ── */
div[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #ddd;
}

/* ── buttons ── */
div.stDownloadButton > button {
    background-color: #e94560 !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
}
div.stDownloadButton > button:hover {
    background-color: #c73652 !important;
}

/* ── alert boxes ── */
div[data-testid="stAlert"] {
    border-radius: 10px;
}

/* ── top banner ── */
.top-banner {
    background: linear-gradient(90deg, #1a1a2e, #0f3460, #e94560);
    padding: 24px 30px;
    border-radius: 14px;
    margin-bottom: 20px;
    color: white;
}
.top-banner h1 {
    margin: 0;
    font-size: 2rem;
    color: white;
}
.top-banner p {
    margin: 4px 0 0;
    opacity: 0.8;
    font-size: 0.9rem;
}

.badge {
    background: #e94560;
    color: white;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div class="top-banner">
    <span class="badge">Mini Project — CSE Sem 4</span>
    <h1>💸 Bank Transaction Analyzer</h1>
    <p>Upload your bank CSV and get instant analysis, charts & anomaly detection!</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SAMPLE CSV HELPER
# ─────────────────────────────────────────────
SAMPLE_CSV = """TransactionID,Date,Amount,Type,Description
TXN001,2024-01-05,12000,Credit,Salary
TXN002,2024-01-07,3500,Debit,Rent
TXN003,2024-01-10,800,Debit,Groceries
TXN004,2024-01-15,50000,Credit,Freelance Payment
TXN005,2024-01-18,1200,Debit,Electricity Bill
TXN006,2024-02-01,12000,Credit,Salary
TXN007,2024-02-03,2000,Debit,Shopping
TXN008,2024-02-10,500,Debit,Cafe
TXN009,2024-02-14,9000,Debit,Laptop EMI
TXN010,2024-02-20,300,Debit,Recharge
TXN011,2024-03-01,12000,Credit,Salary
TXN012,2024-03-05,4500,Debit,Rent
TXN013,2024-03-12,75000,Credit,Project Bonus
TXN014,2024-03-15,600,Debit,Food Delivery
TXN015,2024-03-22,1500,Debit,Gym Membership
"""

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Controls")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Bank CSV",
    type=["csv"],
    help="CSV must have: TransactionID, Date, Amount, Type"
)

st.sidebar.markdown("---")
st.sidebar.download_button(
    "📥 Download Sample CSV",
    data=SAMPLE_CSV,
    file_name="sample_transactions.csv",
    mime="text/csv",
    use_container_width=True
)
st.sidebar.info("👆 Download the sample CSV to test the dashboard!")

# ─────────────────────────────────────────────
#  MAIN LOGIC
# ─────────────────────────────────────────────
if uploaded_file is None:
    st.markdown("### 👈 Upload a CSV file from the sidebar to get started")
    st.markdown("""
    **Expected CSV format:**
    | TransactionID | Date | Amount | Type |
    |---|---|---|---|
    | TXN001 | 2024-01-05 | 12000 | Credit |
    | TXN002 | 2024-01-07 | 3500 | Debit |

    > You can also download the **Sample CSV** from the sidebar to try it out!
    """)
    st.stop()

# ── Load & Validate ──────────────────────────
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"❌ Could not read file: {e}")
    st.stop()

required_cols = {"TransactionID", "Date", "Amount", "Type"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"❌ Missing columns: {', '.join(missing)}\n\nYour file has: {', '.join(df.columns)}")
    st.stop()

# ── Clean Data ───────────────────────────────
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])               # drop rows where date couldn't parse
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
df = df.sort_values("Date").reset_index(drop=True)

st.success(f"✅ Loaded **{len(df)}** transactions successfully!")

# ── Sidebar Filters ──────────────────────────
st.sidebar.markdown("### 🔍 Filters")

date_min = df["Date"].min().date()
date_max = df["Date"].max().date()

start_date = st.sidebar.date_input("Start Date", date_min, min_value=date_min, max_value=date_max)
end_date   = st.sidebar.date_input("End Date",   date_max, min_value=date_min, max_value=date_max)

# BUG FIX: was not guarding against start > end
if start_date > end_date:
    st.sidebar.error("Start date can't be after end date!")
    st.stop()

all_types = df["Type"].dropna().unique().tolist()
txn_type = st.sidebar.multiselect(
    "Transaction Type",
    options=all_types,
    default=all_types
)

if not txn_type:
    st.sidebar.warning("Select at least one transaction type.")
    st.stop()

# ── Apply Filters ────────────────────────────
mask = (
    (df["Date"].dt.date >= start_date) &
    (df["Date"].dt.date <= end_date) &
    (df["Type"].isin(txn_type))
)
filtered_df = df[mask].copy()

if filtered_df.empty:
    st.warning("⚠️ No transactions match your filters. Try adjusting the dates or type.")
    st.stop()

# ─────────────────────────────────────────────
#  METRICS
# ─────────────────────────────────────────────
st.markdown("## 📊 Key Metrics")

total_amt  = filtered_df["Amount"].sum()
avg_amt    = filtered_df["Amount"].mean()
max_amt    = filtered_df["Amount"].max()
txn_count  = len(filtered_df)

# BUG FIX: separate credit/debit instead of mixing everything
credits = filtered_df[filtered_df["Type"].str.lower() == "credit"]["Amount"].sum()
debits  = filtered_df[filtered_df["Type"].str.lower() == "debit"]["Amount"].sum()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Total Amount",    f"₹{total_amt:,.0f}")
c2.metric("📈 Total Credits",   f"₹{credits:,.0f}")
c3.metric("📉 Total Debits",    f"₹{debits:,.0f}")
c4.metric("🔢 Transactions",    txn_count)
c5.metric("📌 Avg Transaction", f"₹{avg_amt:,.0f}")

st.markdown("---")

# ─────────────────────────────────────────────
#  CHARTS  (2 columns layout)
# ─────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("### 📈 Daily Transaction Trend")
    # BUG FIX: groupby date (not datetime) to avoid duplicate x-axis points
    daily = (
        filtered_df
        .groupby(filtered_df["Date"].dt.date)["Amount"]
        .sum()
        .reset_index()
    )
    daily.columns = ["Date", "Amount"]
    fig1 = px.line(
        daily, x="Date", y="Amount",
        markers=True,
        color_discrete_sequence=["#e94560"],
        template="plotly_white"
    )
    fig1.update_traces(line_width=2.5, marker_size=6)
    fig1.update_layout(
        margin=dict(t=10, b=10),
        hovermode="x unified",
        yaxis_title="Amount (₹)"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.markdown("### 🔄 Credit vs Debit")
    # BUG FIX: use groupby so it works even with extra types
    type_summary = filtered_df.groupby("Type")["Amount"].sum().reset_index()
    fig2 = px.pie(
        type_summary,
        names="Type",
        values="Amount",
        hole=0.5,
        color_discrete_sequence=["#0f3460", "#e94560", "#533483", "#f5a623"],
        template="plotly_white"
    )
    fig2.update_traces(textinfo="percent+label", pull=[0.03]*len(type_summary))
    fig2.update_layout(margin=dict(t=10, b=10), showlegend=True)
    st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
#  MONTHLY BAR CHART
# ─────────────────────────────────────────────
st.markdown("### 📅 Monthly Summary")

# BUG FIX: dt.to_period returns Period object; .astype(str) works but groupby
# needs consistent types. Use dt.strftime instead — safer.
filtered_df["Month"] = filtered_df["Date"].dt.strftime("%Y-%m")
monthly = filtered_df.groupby(["Month", "Type"])["Amount"].sum().reset_index()

fig3 = px.bar(
    monthly, x="Month", y="Amount", color="Type",
    barmode="group",
    color_discrete_sequence=["#0f3460", "#e94560"],
    template="plotly_white",
    text_auto=".2s"
)
fig3.update_layout(
    margin=dict(t=10, b=10),
    yaxis_title="Amount (₹)",
    xaxis_title="Month"
)
st.plotly_chart(fig3, use_container_width=True)

# Monthly table
monthly_total = filtered_df.groupby("Month")["Amount"].sum().reset_index()
monthly_total.columns = ["Month", "Total Amount (₹)"]
monthly_total["Total Amount (₹)"] = monthly_total["Total Amount (₹)"].apply(lambda x: f"₹{x:,.2f}")
st.dataframe(monthly_total, use_container_width=True, hide_index=True)

st.markdown("---")

# ─────────────────────────────────────────────
#  ANOMALY DETECTION
# ─────────────────────────────────────────────
st.markdown("### 🚨 Anomaly Detection (High Amount Transactions)")

# BUG FIX: std() can be NaN if only 1 row — add a fallback
if len(filtered_df) >= 2:
    mean_amt = filtered_df["Amount"].mean()
    std_amt  = filtered_df["Amount"].std()
    threshold = mean_amt + 2 * std_amt

    anomalies = filtered_df[filtered_df["Amount"] > threshold].copy()
    st.caption(f"Threshold: mean + 2×std = ₹{mean_amt:,.0f} + 2×₹{std_amt:,.0f} = ₹{threshold:,.0f}")

    if not anomalies.empty:
        st.warning(f"⚠️ Found **{len(anomalies)}** unusually high transaction(s)!")
        display_cols = [c for c in ["TransactionID", "Date", "Amount", "Type", "Description"] if c in anomalies.columns]
        st.dataframe(anomalies[display_cols].reset_index(drop=True), use_container_width=True)
    else:
        st.success("✅ No anomalies found — all transactions look normal.")
else:
    st.info("ℹ️ Not enough data for anomaly detection (need at least 2 transactions).")

st.markdown("---")

# ─────────────────────────────────────────────
#  RAW DATA TABLE  (collapsible)
# ─────────────────────────────────────────────
with st.expander("🗃️ View Raw Filtered Data"):
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

# ─────────────────────────────────────────────
#  DOWNLOAD
# ─────────────────────────────────────────────
st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),  # BUG FIX: encode to bytes
    file_name="filtered_transactions.csv",
    mime="text/csv"
)

# ─────────────────────────────────────────────
#  AUTO INSIGHTS
# ─────────────────────────────────────────────
st.markdown("### 🧠 Auto Insights")

# Find busiest month
busiest_month = filtered_df.groupby("Month")["Amount"].sum().idxmax()
busiest_val   = filtered_df.groupby("Month")["Amount"].sum().max()

# Most common type
top_type = filtered_df["Type"].value_counts().idxmax()
top_type_count = filtered_df["Type"].value_counts().max()

net = credits - debits
net_label = "positive (more credits than debits) 🎉" if net >= 0 else "negative (more debits than credits) ⚠️"

st.info(f"""
**Here's what I found in your data:**

- 📅 Busiest month: **{busiest_month}** with ₹{busiest_val:,.0f} in transactions  
- 🏷️ Most common type: **{top_type}** ({top_type_count} times)  
- 💸 Highest single transaction: **₹{max_amt:,.0f}**  
- 📊 Average transaction: **₹{avg_amt:,.0f}**  
- 🔁 Net balance (Credits − Debits): **₹{net:,.0f}** — {net_label}
""")

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.caption("Made with ❤️ using Python + Streamlit | Mini Project CSE | 2024")
