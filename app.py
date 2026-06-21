import os
import pandas as pd
import streamlit as st

from src.triage_engine import analyze_note, format_markdown_brief
from src.evaluation import evaluate_output_against_source
from src.claude_client import claude_available, analyze_with_claude


st.set_page_config(
    page_title="MissionOps Intake Assistant",
    page_icon="🧭",
    layout="wide"
)

st.title("MissionOps Intake Assistant")
st.caption("A human-in-the-loop workflow for turning messy intake notes into structured, reviewable briefs.")

with st.sidebar:
    st.header("Settings")
    use_claude = st.toggle(
        "Use Claude API if available",
        value=False,
        help="Requires ANTHROPIC_API_KEY. The app still works without it using the local rule-based engine."
    )
    st.info("This tool supports staff review. It does not make final decisions.")

tab1, tab2, tab3 = st.tabs(["Generate Intake Brief", "Evaluate Draft Output", "About"])

with tab1:
    st.subheader("1. Load notes")

    source_choice = st.radio(
        "Choose data source",
        ["Use sample data", "Upload CSV"],
        horizontal=True
    )

    if source_choice == "Upload CSV":
        uploaded = st.file_uploader("Upload a CSV with client_id and note columns", type=["csv"])
        if uploaded:
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_csv("sample_data/intake_notes.csv")
            st.warning("No file uploaded yet. Showing sample data.")
    else:
        df = pd.read_csv("sample_data/intake_notes.csv")

    required_cols = {"client_id", "note"}
    if not required_cols.issubset(set(df.columns)):
        st.error("CSV must include at least client_id and note columns.")
        st.stop()

    st.dataframe(df, use_container_width=True)

    st.subheader("2. Select a note")
    selected_id = st.selectbox("Client ID", df["client_id"].astype(str).tolist())
    row = df[df["client_id"].astype(str) == selected_id].iloc[0]
    note = str(row["note"])

    st.text_area("Source note", note, height=180)

    st.subheader("3. Generate structured brief")

    if st.button("Generate brief", type="primary"):
        if use_claude and claude_available():
            try:
                result = analyze_with_claude(note)
                st.success("Generated with Claude API.")
                st.markdown(result)
            except Exception as exc:
                st.warning(f"Claude API mode failed, so the app used the local fallback. Error: {exc}")
                analysis = analyze_note(note)
                st.markdown(format_markdown_brief(analysis))
        else:
            if use_claude and not claude_available():
                st.warning("ANTHROPIC_API_KEY not found. Using local rule-based engine.")
            analysis = analyze_note(note)
            st.markdown(format_markdown_brief(analysis))

with tab2:
    st.subheader("Evaluate a draft against source notes")
    st.write("Paste a source note and an AI-generated draft. The evaluator checks for unsupported claims, missing-information handling, and basic source alignment.")

    eval_source = st.text_area("Source note", height=160, key="eval_source")
    eval_draft = st.text_area("Draft output to evaluate", height=220, key="eval_draft")

    if st.button("Evaluate draft"):
        if not eval_source.strip() or not eval_draft.strip():
            st.error("Please provide both a source note and a draft output.")
        else:
            report = evaluate_output_against_source(eval_source, eval_draft)
            st.markdown(report)

with tab3:
    st.subheader("About this prototype")
    st.markdown(
        """
        This is a working prototype for mission-driven organizations that need better ways to structure intake notes while keeping staff in control.

        **Core design choice:** AI helps organize information, but humans review and decide.

        **Best-fit use cases:**
        - Workforce development intake
        - Student support programs
        - Civic service navigation
        - Food, housing, or employment resource coordination
        - Program follow-up summaries

        **Not appropriate for:**
        - Automated eligibility decisions
        - Medical diagnosis
        - Legal advice
        - Crisis response without trained staff involvement
        """
    )
