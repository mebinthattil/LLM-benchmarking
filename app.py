import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="LLM Benchmark Viewer", layout="wide")

file_path = "LLM benchmarking - Sugar.xlsx"

# Load Excel
xl = pd.ExcelFile(file_path)
st.sidebar.header("Models Available")
st.sidebar.write(xl.sheet_names)

all_data = []

for sheet in xl.sheet_names:
    df = xl.parse(sheet)
    questions = df.iloc[7::2, 0].reset_index(drop=True)
    responses = df.iloc[7::2, 1].reset_index(drop=True)
    for q, r in zip(questions, responses):
        if pd.notna(q) and pd.notna(r):
            all_data.append({
                "Model": sheet,
                "Question": q.strip(),
                "Response": r.strip(),
                "Word Count": len(r.strip().split()),
                "Emoji Count": len(re.findall(r'[^\w\s,]', r))
            })

df_all = pd.DataFrame(all_data)

# Tabs
tab1, tab2 = st.tabs(["📊 Summary Report", "📋 All Responses"])

with tab1:
    st.subheader("Model Performance Summary")
    summary = df_all.groupby("Model").agg({
        "Response": "count",
        "Word Count": "mean",
        "Emoji Count": "sum"
    }).rename(columns={
        "Response": "Number of Responses",
        "Word Count": "Avg Words/Response",
        "Emoji Count": "Total Emojis"
    }).sort_values(by="Avg Words/Response", ascending=False)
    st.dataframe(summary, use_container_width=True)

    best_tradeoff = summary["Avg Words/Response"].idxmax()
    st.success(f"🎯 **Best trade-off of size and quality:** `{best_tradeoff}`")

with tab2:
    st.subheader("All Model Outputs")
    selected_model = st.selectbox("Choose a model", df_all["Model"].unique())
    filtered = df_all[df_all["Model"] == selected_model]
    for _, row in filtered.iterrows():
        st.markdown(f"**Q:** {row['Question']}")
        st.markdown(f"> 💬 {row['Response']}")
        st.markdown("---")
