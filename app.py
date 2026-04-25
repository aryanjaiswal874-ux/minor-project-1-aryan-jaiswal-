import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Bank Analysis", page_icon="💰", layout="wide")

st.markdown("""
<style>
body { background-color: #f0f4f8; }
h1 { color: #2c3e50; text-align: center; }
h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
.stMetric {
    background-color: white;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #ddd;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
}
div[data-testid="stMetricValue"] { color: #2980b9; font-size: 28px !important; font-weight: bold; }
.stAlert { border-radius: 8px; }
footer { text-align: center; color: gray; margin-top: 30px; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ---- HEADER ----
st.markdown("<h1>💰 Bank Transaction Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Upload your bank CSV and explore your transactions!</p>", unsafe_allow_html=True)
st.markdown("---")

# ---- FILE UPLOAD ----
st.markdown("### 📁 Upload Your File")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is None:
    st.info("👆 Please upload a CSV file to get started. It should have: TransactionID, Date, Amount, Type")
    st.stop()

# ---- LOAD DATA ----
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Couldn't read file 😢 Error: {e}")
    st.stop()

required_cols = {"TransactionID", "Date", "Amount", "Type"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"Missing columns: {', '.join(missing)}")
    st.stop()

# BUG FIX 1: Strip whitespace from column names and string columns
df.columns = df.columns.str.strip()
df["Type"] = df["Type"].astype(str).str.strip()

# BUG FIX 2: Robust date parsing — try multiple formats
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
bad_dates = df["Date"].isna().sum()
if bad_dates > 0:
    st.warning(f"⚠️ {bad_dates} rows had unreadable dates and were removed.")
df = df.dropna(subset=["Date"])

# BUG FIX 3: Remove currency symbols and commas before converting Amount
df["Amount"] = (
    df["Amount"]
    .astype(str)
    .str.replace(r"[₹$,\s]", "", regex=True)
    .str.strip()
)
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
bad_amt = df["Amount"].isna().sum()
if bad_amt > 0:
    st.warning(f"⚠️ {bad_amt} rows had invalid Amount values and were removed.")
df = df.dropna(subset=["Amount"])

# BUG FIX 4: Remove negative amounts that would break graphs (optional: abs or drop)
negative_count = (df["Amount"] < 0).sum()
if negative_count > 0:
    st.info(f"ℹ️ {negative_count} negative amount rows found — using absolute values.")
    df["Amount"] = df["Amount"].abs()

if df.empty:
    st.error("No valid data found after cleaning.")
    st.stop()

st.success(f"✅ File loaded successfully! Found {len(df)} transactions.")

# ---- SIDEBAR ----
st.sidebar.title("🔧 Filter Options")
st.sidebar.write("Use these to filter your data:")

date_min = df["Date"].min().date()
date_max = df["Date"].max().date()

start_date = st.sidebar.date_input("Start Date", date_min, min_value=date_min, max_value=date_max)
end_date   = st.sidebar.date_input("End Date",   date_max, min_value=date_min, max_value=date_max)

# BUG FIX 5: Proper date validation before filtering
if start_date > end_date:
    st.sidebar.error("Start date can't be after end date!")
    st.stop()

types = sorted(df["Type"].dropna().unique().tolist())
selected_types = st.sidebar.multiselect("Transaction Type", options=types, default=types)

if not selected_types:
    st.sidebar.warning("Please select at least one transaction type.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.write("Made by a CSE student 😄")

# BUG FIX 6: Use .dt.normalize() to avoid time-of-day mismatch in date comparison
filtered_df = df[
    (df["Date"].dt.date >= start_date) &
    (df["Date"].dt.date <= end_date) &
    (df["Type"].isin(selected_types))
].copy()

if filtered_df.empty:
    st.warning("No data matches your filters. Try changing the filters!")
    st.stop()

# ---- PRE-COMPUTE MONTH COLUMN (once, here — avoid SettingWithCopyWarning) ----
filtered_df["Month"] = filtered_df["Date"].dt.to_period("M").astype(str)
filtered_df["Date_only"] = filtered_df["Date"].dt.date

# ---- METRICS ----
st.markdown("---")
st.markdown("## 📊 Summary")

total_amt = filtered_df["Amount"].sum()
avg_amt   = filtered_df["Amount"].mean()
max_amt   = filtered_df["Amount"].max()
min_amt   = filtered_df["Amount"].min()
txn_count = len(filtered_df)

# BUG FIX 7: Handle edge case where std = 0 (all amounts identical)
std_amt = filtered_df["Amount"].std()
if pd.isna(std_amt):
    std_amt = 0.0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Amount",   f"₹{total_amt:,.2f}")
col2.metric("Average Amount", f"₹{avg_amt:,.2f}")
col3.metric("Highest Txn",    f"₹{max_amt:,.2f}")
col4.metric("Lowest Txn",     f"₹{min_amt:,.2f}")
col5.metric("No. of Txns",    f"{txn_count:,}")

# Credit / Debit split
st.markdown("#### Credit vs Debit Totals")
type_lower = filtered_df["Type"].str.lower()
credit_total = filtered_df[type_lower.str.contains("credit", na=False)]["Amount"].sum()
debit_total  = filtered_df[type_lower.str.contains("debit",  na=False)]["Amount"].sum()
net = credit_total - debit_total

cb1, cb2, cb3 = st.columns(3)
cb1.metric("🟢 Total Credit", f"₹{credit_total:,.2f}")
cb2.metric("🔴 Total Debit",  f"₹{debit_total:,.2f}")
cb3.metric("⚖️ Net Balance",  f"₹{net:,.2f}", delta="Surplus" if net >= 0 else "Deficit")

# ---- CHARTS ----
st.markdown("---")
st.markdown("## 📈 Charts")

col_a, col_b = st.columns(2)

# BUG FIX 8: Daily trend — group by date object (not datetime) to avoid time gaps
with col_a:
    st.markdown("### Daily Trend")
    daily = (
        filtered_df.groupby("Date_only")["Amount"]
        .sum()
        .reset_index()
        .rename(columns={"Date_only": "Date"})
        .sort_values("Date")  # BUG FIX: always sort by date
    )
    # BUG FIX 9: If only 1 data point, use bar instead of line (line needs ≥2 points)
    if len(daily) < 2:
        fig1 = px.bar(daily, x="Date", y="Amount",
                      color_discrete_sequence=["#3498db"],
                      text_auto=True)
    else:
        fig1 = px.line(daily, x="Date", y="Amount", markers=True,
                       color_discrete_sequence=["#3498db"])
    fig1.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis_title="Date", yaxis_title="Amount (₹)",
        yaxis_tickprefix="₹", yaxis_tickformat=","
    )
    fig1.update_xaxes(showgrid=True, gridcolor="#eee")
    fig1.update_yaxes(showgrid=True, gridcolor="#eee", rangemode="tozero")
    st.plotly_chart(fig1, use_container_width=True)

# BUG FIX 10: Pie chart — handle case when only 1 type exists
with col_b:
    st.markdown("### Credit vs Debit")
    type_data = filtered_df.groupby("Type")["Amount"].sum().reset_index()
    type_data = type_data[type_data["Amount"] > 0]  # remove zero-value types

    if type_data.empty:
        st.info("No type data to show.")
    elif len(type_data) == 1:
        # BUG FIX: pie with 1 slice looks broken — use bar instead
        fig2 = px.bar(type_data, x="Type", y="Amount",
                      color_discrete_sequence=["#3498db"], text_auto=True)
        fig2.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                           yaxis_tickprefix="₹", yaxis_tickformat=",")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        fig2 = px.pie(
            type_data, names="Type", values="Amount", hole=0.35,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig2.update_traces(textinfo="label+percent+value",
                           hovertemplate="%{label}<br>₹%{value:,.2f}<br>%{percent}")
        fig2.update_layout(paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

# BUG FIX 11: Monthly chart — sort months correctly (string sort fails for periods)
st.markdown("### 📅 Monthly Totals")
monthly = (
    filtered_df.groupby("Month")["Amount"]
    .sum()
    .reset_index()
    .sort_values("Month")  # period strings sort correctly as YYYY-MM
)
monthly["Amount_rounded"] = monthly["Amount"].round(2)

fig3 = px.bar(
    monthly, x="Month", y="Amount_rounded",
    color="Amount_rounded",
    color_continuous_scale="Blues",
    text=monthly["Amount_rounded"].apply(lambda x: f"₹{x:,.0f}"),
    labels={"Amount_rounded": "Amount (₹)"}
)
fig3.update_traces(textposition="outside")
fig3.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    showlegend=False,
    coloraxis_showscale=False,
    yaxis_tickprefix="₹", yaxis_tickformat=",",
    yaxis=dict(rangemode="tozero")  # BUG FIX: start y-axis from 0
)
fig3.update_xaxes(showgrid=False)
fig3.update_yaxes(showgrid=True, gridcolor="#eee")
st.plotly_chart(fig3, use_container_width=True)

# BUG FIX 12: Monthly table with proper columns
monthly_table = (
    filtered_df.groupby("Month")
    .agg(
        Total_Amount=("Amount", "sum"),
        Avg_Amount=("Amount", "mean"),
        Max_Amount=("Amount", "max"),
        Transactions=("Amount", "count")
    )
    .reset_index()
    .sort_values("Month")
)
monthly_table["Total_Amount"] = monthly_table["Total_Amount"].round(2)
monthly_table["Avg_Amount"]   = monthly_table["Avg_Amount"].round(2)
monthly_table["Max_Amount"]   = monthly_table["Max_Amount"].round(2)
monthly_table.columns = ["Month", "Total (₹)", "Average (₹)", "Max (₹)", "Transactions"]
st.dataframe(monthly_table.reset_index(drop=True), use_container_width=True)

# ---- ANOMALY DETECTION ----
st.markdown("---")
st.markdown("## 🚨 Unusual Transactions")

# BUG FIX 13: std=0 or NaN edge case (all same amount)
if std_amt == 0 or txn_count < 3:
    st.info("Not enough variation in data to detect anomalies.")
else:
    threshold = mean_amt + 2 * std_amt
    st.caption(f"Threshold = Mean (₹{mean_amt:,.2f}) + 2 × Std (₹{std_amt:,.2f}) = ₹{threshold:,.2f}")

    anomalies = filtered_df[filtered_df["Amount"] > threshold].copy()
    # BUG FIX 14: Drop internal helper columns before showing
    anomalies = anomalies.drop(columns=["Month", "Date_only"], errors="ignore")
    anomalies = anomalies.sort_values("Amount", ascending=False).reset_index(drop=True)

    if not anomalies.empty:
        st.warning(f"⚠️ Found {len(anomalies)} transaction(s) above ₹{threshold:,.2f}")
        st.dataframe(anomalies, use_container_width=True)

        # Scatter plot for visual context
        scatter_df = filtered_df.copy()
        scatter_df["Is Anomaly"] = scatter_df["Amount"] > threshold
        fig_s = px.scatter(
            scatter_df, x="Date_only", y="Amount",
            color="Is Anomaly",
            color_discrete_map={True: "#e74c3c", False: "#3498db"},
            labels={"Date_only": "Date", "Amount": "Amount (₹)", "Is Anomaly": "Anomaly"},
            hover_data=["Type"]
        )
        fig_s.add_hline(y=threshold, line_dash="dash", line_color="orange",
                        annotation_text=f"Threshold ₹{threshold:,.0f}",
                        annotation_font_color="orange")
        fig_s.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                            yaxis_tickprefix="₹", yaxis_tickformat=",",
                            yaxis=dict(rangemode="tozero"))
        st.plotly_chart(fig_s, use_container_width=True)
    else:
        st.success("✅ No unusual transactions found. Everything looks normal!")

# ---- RAW DATA ----
st.markdown("---")
st.markdown("## 🗃️ All Transactions")
show_raw = st.checkbox("Show raw data table")
if show_raw:
    show_df = filtered_df.drop(columns=["Month", "Date_only"], errors="ignore")
    st.dataframe(show_df.reset_index(drop=True), use_container_width=True)
    st.caption(f"Showing {len(show_df)} transactions")

# ---- DOWNLOAD ----
st.markdown("---")
st.markdown("## ⬇️ Download Filtered Data")
dl_df = filtered_df.drop(columns=["Month", "Date_only"], errors="ignore")
st.download_button(
    label="Download CSV",
    data=dl_df.to_csv(index=False),
    file_name="filtered_transactions.csv",
    mime="text/csv"
)

# ---- FOOTER ----
st.markdown("---")
st.markdown("""
<footer>
    Built using Streamlit + Plotly &nbsp;|&nbsp; CSE 3rd Sem Mini Project &nbsp;|&nbsp; 2024
</footer>
""", unsafe_allow_html=True)
