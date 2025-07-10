import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the dataset
!git clone https://github.com/PhonePe/pulse.git
import os
import json
data=[]
root="pulse/data/aggregated/transaction/country/india/state"
for state in os.listdir(root):
    for year in os.listdir(f"{root}/{state}"):
        for file in os.listdir(f"{root}/{state}/{year}"):
            path=f"{root}/{state}/{year}/{file}"
            with open(path) as f:
                d=json.load(f).get("data", {}).get("transactionData", [])
            q=int(file.replace(".json",""))
            for e in d:
                data.append({
                    "state": state.replace("-", " ").title(),
                    "year": int(year),
                    "quarter": q,
                    "transaction_type": e["name"],
                    "count": e["paymentInstruments"][0]["count"],
                    "amount": e["paymentInstruments"][0]["amount"]
                })
df = pd.DataFrame(data)

st.set_page_config(page_title="PhonePe Pulse Dashboard", layout="wide")

st.title(" PhonePe Pulse - Transaction Analysis Dashboard")

# Sidebar filters
st.sidebar.header("Filter Options")
years = sorted(df["year"].unique())
quarters = sorted(df["quarter"].unique())
states = sorted(df["state"].unique())
txn_types = sorted(df["transaction_type"].unique())

selected_year = st.sidebar.multiselect("Select Year", years, default=years)
selected_quarter = st.sidebar.multiselect("Select Quarter", quarters, default=quarters)
selected_state = st.sidebar.multiselect("Select State", states, default=states)
selected_type = st.sidebar.multiselect("Select Transaction Type", txn_types, default=txn_types)

# Apply filters
filtered_df = df[
    (df["year"].isin(selected_year)) &
    (df["quarter"].isin(selected_quarter)) &
    (df["state"].isin(selected_state)) &
    (df["transaction_type"].isin(selected_type))
]

# Key Metrics
st.subheader(" Key Metrics")
col1, col2 = st.columns(2)

with col1:
    st.metric("Total Transactions", f"{filtered_df['count'].sum():,}")
with col2:
    st.metric("Total Amount (₹)", f"{filtered_df['amount'].sum():,.2f}")

# Charts

# 1. Transactions per Year
st.subheader(" Total Transactions Per Year")
year_df = filtered_df.groupby("year")["count"].sum().reset_index()
fig1, ax1 = plt.subplots()
sns.barplot(data=year_df, x="year", y="count", ax=ax1, palette="Blues_d")
ax1.set_ylabel("Total Transactions")
st.pyplot(fig1)

# 2. Amount by State
st.subheader(" Top 10 States by Transaction Amount")
top_states = filtered_df.groupby("state")["amount"].sum().nlargest(10).reset_index()
fig2, ax2 = plt.subplots()
sns.barplot(data=top_states, y="state", x="amount", ax=ax2, palette="viridis")
ax2.set_xlabel("Amount (₹)")
st.pyplot(fig2)

# 3. Pie chart of Transaction Type Distribution
st.subheader(" Transaction Type Distribution")
type_df = filtered_df.groupby("transaction_type")["count"].sum()
fig3, ax3 = plt.subplots()
type_df.plot(kind="pie", autopct="%1.1f%%", ax=ax3, ylabel="")
st.pyplot(fig3)

# 4. Heatmap - Quarterly Activity by State
st.subheader(" State vs Quarter Heatmap (Amount)")
pivot = filtered_df.pivot_table(index="state", columns="quarter", values="amount", aggfunc="sum", fill_value=0)
fig4, ax4 = plt.subplots(figsize=(10, 12))
sns.heatmap(pivot, cmap="YlGnBu", linewidths=0.5, ax=ax4)
st.pyplot(fig4)

# 5. Scatter Plot - Count vs Amount
st.subheader(" Count vs Amount Scatter Plot")
fig5, ax5 = plt.subplots()
sns.scatterplot(data=filtered_df, x="count", y="amount", hue="transaction_type", ax=ax5)
st.pyplot(fig5)

# 6. Correlation Heatmap
st.subheader(" Correlation Heatmap")
fig6, ax6 = plt.subplots()
sns.heatmap(filtered_df[["count", "amount"]].corr(), annot=True, cmap="coolwarm", ax=ax6)
st.pyplot(fig6)

# 7. Year-wise Quarterly Trend
st.subheader(" Quarterly Trend by Year")
fig7, ax7 = plt.subplots()
sns.lineplot(data=filtered_df, x="quarter", y="amount", hue="year", marker="o", ax=ax7)
st.pyplot(fig7)

# Footer
st.markdown("---")
st.markdown(" Built with Streamlit |  Source: [PhonePe Pulse GitHub](https://github.com/PhonePe/pulse)")
