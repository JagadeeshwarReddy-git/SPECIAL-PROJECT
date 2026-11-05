
import json
import pandas as pd
import streamlit as st
import ollama


MODEL = "llama3.2"

# Connect to the local Ollama server.
client = ollama.Client(
    host="http://127.0.0.1:11434"
)


def _build_analysis_context(
    df,
    analysis_type,
    context=None,
):
    """Create a compact, factual description of completed results."""

    if df is None or not isinstance(df, pd.DataFrame):
        return {
            "analysis_type": analysis_type,
            "context": context or {},
            "error": "No DataFrame was provided.",
        }

    result = {
        "analysis_type": analysis_type,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": list(df.columns),
        "context": context or {},
    }

    if df.empty:
        result["message"] = "The DataFrame contains no rows."
        return result

    # Numeric statistics.
    numeric = df.select_dtypes(include="number")

    if not numeric.empty:
        result["numeric_statistics"] = (
            numeric.describe()
            .round(3)
            .replace({float("nan"): None})
            .to_dict()
        )

    # Important category distributions.
    categorical = {}

    for column in df.columns:
        if column in numeric.columns:
            continue

        values = df[column].dropna()

        if values.empty:
            continue

        categorical[str(column)] = {
            "unique_values": int(values.nunique()),
            "most_common": {
                str(key): int(value)
                for key, value in
                values.astype(str).value_counts().head(10).items()
            },
        }

    result["categorical_distributions"] = categorical

    # Include only a small sample, not the entire dataset.
    sample = df.head(12).copy()

    sample = sample.astype(object).where(
        pd.notna(sample),
        None,
    )

    result["sample_rows"] = sample.to_dict(
        orient="records"
    )

    return result


def generate_analysis_explanation(
    df,
    analysis_type="Analysis",
    context=None,
):
    """
    Explain completed analysis results using local Ollama.

    The model receives analysis results and a limited sample.
    It must distinguish observed findings from uncertainty.
    """

    analysis_context = _build_analysis_context(
        df,
        analysis_type,
        context,
    )

    if analysis_context.get("error"):
        return (
            "An explanation cannot be generated because "
            "the analysis results are unavailable."
        )

    if analysis_context.get("row_count", 0) == 0:
        return (
            "The analysis contains no records. Add data and "
            "run the analysis before requesting an explanation."
        )

    prompt = f"""
Explain the completed {analysis_type} results below.

ANALYSIS RESULTS:
{json.dumps(analysis_context, ensure_ascii=False, default=str)}

Write a clear explanation using these sections:

## 1. What this analysis is about
Explain the purpose of this analysis based on the supplied data.

## 2. Main findings
Describe the most important patterns and results supported by
the provided statistics, category distributions, and sample rows.

## 3. What the results mean
Explain the practical meaning of the findings in straightforward
language. Explain relevant metrics when possible.

## 4. Important observations
Identify notable differences, imbalances, unusual values, or
potential issues only when the supplied data supports them.

## 5. Limitations
Mention missing information or conclusions that cannot be
established from the supplied results.

## 6. Key takeaway
Provide a concise conclusion based on the available evidence.

STRICT RULES:
- Base claims on the supplied analysis results.
- Do not invent facts, metrics, causes, or trends.
- Do not claim correlation proves causation.
- Do not describe a trend unless the data supports it.
- Do not repeat the sample rows as the explanation.
- Explain what the findings mean rather than simply listing values.
- If a field's meaning is unclear, state that limitation.
- Never claim to have inspected data that was not provided.
- Keep the explanation useful and specific to this analysis.
"""

    try:
        response = client.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful data analyst. "
                        "Explain results clearly and accurately. "
                        "Never invent evidence or conclusions."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        explanation = (
            response.get("message", {})
            .get("content", "")
            .strip()
        )

        if not explanation:
            return "The AI returned an empty explanation. Try again."

        return explanation

    except Exception as exc:
        return (
            "The analysis completed, but its AI explanation "
            "could not be generated.\n\n"
            f"Technical details: {exc}\n\n"
            "Check that Ollama is running and that the "
            f"'{MODEL}' model is installed."
        )


def render_analysis_explanation(
    df,
    analysis_type="Analysis",
    context=None,
    key="analysis_explanation",
):
    """Display an explanation after an analysis has completed."""

    st.subheader("🧠 AI Explanation")

    st.caption(
        "This explanation is generated from the completed analysis "
        "results, not by repeating the input data."
    )

    button_key = f"{key}_generate"
    result_key = f"{key}_result"

    if st.button(
        "✨ Generate Explanation",
        key=button_key,
        type="primary",
    ):
        with st.spinner(
            f"Explaining your {analysis_type.lower()} results..."
        ):
            explanation = generate_analysis_explanation(
                df=df,
                analysis_type=analysis_type,
                context=context,
            )

        st.session_state[result_key] = explanation

    explanation = st.session_state.get(result_key)

    if explanation:
        st.markdown(explanation)

        st.download_button(
            "⬇️ Download Explanation",
            data=explanation,
            file_name=(
                f"{analysis_type.lower().replace(' ', '_')}_"
                "explanation.md"
            ),
            mime="text/markdown",
            key=f"{key}_download",
        )
    else:
        st.info(
            "Complete the analysis, then click Generate Explanation."
        )
