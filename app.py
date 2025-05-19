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

# Add a new tab for Detailed Report
tab3 = st.tabs(["📖 Detailed Report"])[0]

with tab3:
    st.subheader("Detailed Model Behavior Report")
    st.markdown("""
    Below is a detailed breakdown of each model’s behavior on the “friendly robot for children” prompt set, along with key quantitative metrics and qualitative observations. At the end you’ll find our recommendation for the best size‑vs‑quality trade‑off.

    | Model                              | Params (B) | # Responses | Avg. Words/Response | Emojis Used |
    | ---------------------------------- | ---------- | ----------- | ------------------- | ----------- |
    | **Qwen3‑235B‑A22B**                | 235        | 50          | 17.6                | 6           |
    | **Qwen3‑30B‑A3B**                  | 30         | 50          | 17.8                | 0           |
    | **Gemma‑3‑27B**                    | 27         | 50          | 13.2                | 1           |
    | **Mistral‑Small‑3.1‑24B‑Instruct** | 24         | 48          | 12.0                | 0           |
    | **Qwen3‑0.6B**                     | 0.6        | 49          | 5.6                 | 0           |

    ---

    ## 1. Qwen3‑235B‑A22B (235 B parameters)

    **Quantitative:**

    * Long, richly detailed answers (∼17.6 words each)
    * Occasionally injects child‑friendly emojis (6 total)

    **Qualitative Strengths:**

    * **Clarity & Playfulness:** Uses vivid analogies (“like magic paint in the sky 🎨”) that engage children.
    * **Completeness:** Full—even bonus—explanations (e.g. mentions both sunlight and air scattering).

    **Weaknesses:**

    * **Over-verbosity:** Some answers are a bit longer than needed for a young audience.
    * **Compute Cost:** Full 235 B footprint; high inference latency and resource use.

    ---

    ## 2. Qwen3‑30B‑A3B (30 B parameters)

    **Quantitative:**

    * Slightly more compact than 235 B but nearly identical length (∼17.8 words).
    * No emoji use, but crisp, clear phrasing.

    **Qualitative Strengths:**

    * **Very High Fidelity:** Correct, concise, and grammatically clean.
    * **Child‑Appropriate Tone:** Simplifies technical ideas without oversimplifying.

    **Weaknesses:**

    * **Slightly Less Playful:** Lacks the playful emoji garnish, but still friendly.

    ---

    ## 3. Gemma‑3‑27B (27 B parameters)

    **Quantitative:**

    * Medium length (∼13.2 words), down about 25% from the largest models.
    * Rare emoji use (1 total).

    **Qualitative Strengths:**

    * **Efficient Answers:** Gets to the point quickly, good for basic explanations.
    * **Low Latency:** Smaller size yields faster responses.

    **Weaknesses:**

    * **Omitted Nuance:** Sometimes skips extra context (e.g., doesn’t always mention both sunlight and air scattering for sky color).
    * **Less Engaging:** Tone is neutral, not as warm or playful.

    ---

    ## 4. Mistral‑Small‑3.1‑24B‑Instruct (24 B parameters)

    **Quantitative:**

    * Concise responses (∼12 words).
    * Perfectly correct but lean.

    **Qualitative Strengths:**

    * **Precision:** Direct, textbook‑style answers.
    * **Very Fast:** Small footprint.

    **Weaknesses:**

    * **Too Spartan for Kids:** Lacks friendly tone, no extra analogies or playfulness.
    * **Shortfall in Detail:** Some answers are barely more than a keyword.

    ---

    ## 5. Qwen3‑0.6B (0.6 B parameters)

    **Quantitative:**

    * Very short (∼5.6 words), often fragmentary.

    **Qualitative Strengths:**

    * **Speed & Footprint:** Tiny model, ultra‑low memory/compute.

    **Weaknesses:**
    * **Wrong answers**: Some answers are straight up wrong, like "Yes, the moon is made out of cheese", let's just not use this
    * **Insufficient Detail:** Answers are sometimes ambiguous or incomplete.
    * **Occasional Errors:** Misspellings or grammatical hiccups.

    ---

    ## Best Size–Quality Trade‑off

    **Qwen3‑30B‑A3B** emerges as the sweet spot. At just 1/8th the size of the 235 B model, it **matches** its clarity and breadth of explanation (avg. word count nearly identical), with clean grammar and no drop in correctness—yet runs **much** faster and with far lower infrastructure cost.

    **Runner‑up:** Gemma‑3‑27B offers good efficiency, but its shorter, more neutral tone feels less engaging for young learners compared to the 30 B model.
    
    """)
