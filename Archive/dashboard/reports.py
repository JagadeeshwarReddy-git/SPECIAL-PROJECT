import streamlit as st

def show():

    st.title("📄 Reports")

    if "analysis_df" not in st.session_state:
        st.warning("No analysis available. Please analyze a YouTube video or upload a CSV first.")
        return

    df = st.session_state["analysis_df"]

    st.subheader("Summary")

    positive = len(df[df["sentiment"] == "positive"])
    neutral = len(df[df["sentiment"] == "neutral"])
    negative = len(df[df["sentiment"] == "negative"])

    st.metric("Total Comments", len(df))
    st.metric("Positive", positive)
    st.metric("Neutral", neutral)
    st.metric("Negative", negative)

    st.divider()

    if st.button("📄 Generate PDF Report"):

        pdf_file = generate_pdf(df)

        with open(pdf_file, "rb") as file:

            st.download_button(
                label="⬇ Download PDF",
                data=file,
                file_name="AI_Report.pdf",
                mime="application/pdf"
            )

    st.divider()

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Download CSV",
        data=csv,
        file_name="analysis.csv",
        mime="text/csv"
    )