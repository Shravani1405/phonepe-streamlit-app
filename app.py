import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import json

st.set_page_config(page_title="PhonePe Pulse Dashboard", layout="wide")
st.title(" PhonePe Pulse Data Visualization")

DATA_PATH = "pulse/data/aggregated/transaction/country/india/state/"


@st.cache_data
def load_data():
    all_data = []

    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()  # Fail gracefully

    for state in os.listdir(DATA_PATH):
        state_path = os.path.join(DATA_PATH, state)
        if not os.path.isdir(state_path):
            continue
        for year in os.listdir(state_path):
            year_path = os.path.join(state_path, year)
            for quarter_file in os.listdir(year_path):
                file_path = os.path.join(year_path, quarter_file)
                with open(file_path, 'r') as f:
                    try:
                        json_data = json.load(f)
                        records = json_data.get('data', {}).get('transactionData', [])
                        for entry in records:
                            txn_type = entry['name']
                            count = entry['paymentInstruments'][0]['count']
                            amount = entry['paymentInstruments'][0]['amount']
                            all_data.append({
                                'state': state,
                                'year': int(year),
                                'quarter': int(quarter_file.strip('.json')),
                                'transaction_type': txn_type,
                                'count': count,
                                'amount': amount
                            })
                    except Exception as e:
                        print(f"Skipping {file_path}: {e}")
    return pd.DataFrame(all_data)


df = load_data()

if df.empty:
    st.warning(" Data not found! Using sample dataset for demo.")
    df = pd.DataFrame({
        'state': ['Karnataka', 'Maharashtra', 'Delhi', 'Tamil Nadu'],
        'year': [2021, 2021, 2022, 2022],
        'quarter': [1, 2, 3, 4],
        'transaction_type': ['Recharge & bill payments'] * 4,
        'count': [1000, 1500, 2000, 2500],
        'amount': [1e6, 1.5e6, 2e6, 2.5e6]
    })


st.sidebar.header(" Filter Options")
years = sorted(df["year"].unique())
quarters = sorted(df["quarter"].unique())
states = sorted(df["state"].unique())
txn_types = sorted(df["transaction_type"].unique())

selected_year = st.sidebar.multiselect("Select Year", years, default=years)
selected_quarter = st.sidebar.multiselect("Select Quarter", quarters, default=quarters)
selected_state = st.sidebar.multiselect("Select State", states, default=states)
selected_type = st.sidebar.multiselect("Select Transaction Type", txn_types, default=txn_types)

filtered_df = df[
    (df["year"].isin(selected_year)) &
    (df["quarter"].isin(selected_quarter)) &
    (df["state"].isin(selected_state)) &
    (df["transaction_type"].isin(selected_type))
]


st.subheader(" Key Metrics")
col1, col2 = st.columns(2)
col1.metric("Total Transactions", f"{filtered_df['count'].sum():,}")
col2.metric("Total Amount (₹)", f"{filtered_df['amount'].sum():,.2f}")


st.subheader(" Transactions Per Year")
year_df = filtered_df.groupby("year")["count"].sum().reset_index()
fig1, ax1 = plt.subplots()
sns.barplot(data=year_df, x="year", y="count", ax=ax1, palette="Blues_d")
st.pyplot(fig1)

st.subheader(" Top 10 States by Transaction Amount")
top_states = filtered_df.groupby("state")["amount"].sum().nlargest(10).reset_index()
fig2, ax2 = plt.subplots()
sns.barplot(data=top_states, y="state", x="amount", ax=ax2, palette="viridis")
st.pyplot(fig2)

st.subheader(" Transaction Type Distribution")
type_df = filtered_df.groupby("transaction_type")["count"].sum()
fig3, ax3 = plt.subplots()
type_df.plot(kind="pie", autopct="%1.1f%%", ax=ax3, ylabel="")
st.pyplot(fig3)

st.subheader(" State vs Quarter Heatmap (Amount)")
pivot = filtered_df.pivot_table(index="state", columns="quarter", values="amount", aggfunc="sum", fill_value=0)
fig4, ax4 = plt.subplots(figsize=(10, 12))
sns.heatmap(pivot, cmap="YlGnBu", linewidths=0.5, ax=ax4)
st.pyplot(fig4)

st.subheader(" Count vs Amount Scatter Plot")
fig5, ax5 = plt.subplots()
sns.scatterplot(data=filtered_df, x="count", y="amount", hue="transaction_type", ax=ax5)
st.pyplot(fig5)

st.subheader(" Correlation Heatmap")
fig6, ax6 = plt.subplots()
sns.heatmap(filtered_df[["count", "amount"]].corr(), annot=True, cmap="coolwarm", ax=ax6)
st.pyplot(fig6)

st.subheader(" Quarterly Trend by Year")
fig7, ax7 = plt.subplots()
sns.lineplot(data=filtered_df, x="quarter", y="amount", hue="year", marker="o", ax=ax7)
st.pyplot(fig7)

# ------------------- Footer -------------------
st.markdown("---")
st.markdown("Built with  using Streamlit | Source: [PhonePe Pulse GitHub](https://github.com/PhonePe/pulse)")

