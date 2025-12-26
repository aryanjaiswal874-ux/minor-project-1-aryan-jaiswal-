import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Bank Transaction Analysis",
    page_icon="🏦",
    layout="wide"
)

# ---------------- CSS (Modern UI) ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.metric-card {
    background-color: #0f172a;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🏦 Bank Transaction Analysis Dashboard")
st.caption("Advanced analysis with filters, insights & anomaly detection")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload Bank CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = {"TransactionID", "Date", "Amount", "Type"}
    if not required_cols.issubset(df.columns):
        st.error("CSV must contain: TransactionID, Date, Amount, Type")
        st.stop()

    df["Date"] = pd.to_datetime(df["Date"])

    # ---------------- SIDEBAR FILTERS ----------------
    st.sidebar.header("🎛 Filters")

    start_date = st.sidebar.date_input("Start Date", df["Date"].min())
    end_date = st.sidebar.date_input("End Date", df["Date"].max())

    txn_type = st.sidebar.multiselect(
        "Transaction Type",
        options=df["Type"].unique(),
        default=df["Type"].unique()
    )

    filtered_df = df[
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date)) &
        (df["Type"].isin(txn_type))
    ]

    # ---------------- METRICS ----------------
    st.subheader("📊 Key Metrics")

    total_amt = filtered_df["Amount"].sum()
    avg_amt = filtered_df["Amount"].mean()
    max_amt = filtered_df["Amount"].max()
    txn_count = len(filtered_df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Amount", f"₹ {total_amt:,.2f}")
    c2.metric("Average Amount", f"₹ {avg_amt:,.2f}")
    c3.metric("Max Transaction", f"₹ {max_amt:,.2f}")
    c4.metric("Transactions", txn_count)

    # ---------------- DAILY TREND ----------------
    st.subheader("📈 Daily Transaction Trend")
    daily = filtered_df.groupby(filtered_df["Date"].dt.date)["Amount"].sum().reset_index()
    fig1 = px.line(daily, x="Date", y="Amount", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    # ---------------- PIE CHART ----------------
    st.subheader("🔄 Credit vs Debit Share")
    fig2 = px.pie(filtered_df, names="Type", values="Amount", hole=0.45)
    st.plotly_chart(fig2, use_container_width=True)

    # ---------------- MONTHLY SUMMARY ----------------
    st.subheader("📅 Monthly Summary")
    filtered_df["Month"] = filtered_df["Date"].dt.to_period("M").astype(str)
    monthly = filtered_df.groupby("Month")["Amount"].sum().reset_index()
    st.dataframe(monthly, use_container_width=True)

    # ---------------- ANOMALY DETECTION ----------------
    st.subheader("🚨 High Amount Transactions")
    threshold = filtered_df["Amount"].mean() + 2 * filtered_df["Amount"].std()
    anomalies = filtered_df[filtered_df["Amount"] > threshold]

    if not anomalies.empty:
        st.warning("Unusually high transactions detected")
        st.dataframe(anomalies, use_container_width=True)
    else:
        st.success("No abnormal transactions found")

    # ---------------- DOWNLOAD CSV ----------------
    st.download_button(
        "⬇ Download Filtered Data",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_transactions.csv",
        mime="text/csv"
    )

    # ---------------- INSIGHTS ----------------
    st.subheader("🧠 Auto Insights")
    st.success(f"""
    • Highest transaction: ₹{max_amt:,.2f}  
    • Average spending: ₹{avg_amt:,.2f}  
    • Most active period shown in daily trend  
    • Credit/Debit balance visible via pie chart  
    """)

else:
    st.info("📂 Upload CSV to start analysis")
