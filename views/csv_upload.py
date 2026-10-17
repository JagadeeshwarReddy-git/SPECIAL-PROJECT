
import io
import html
import pandas as pd
import streamlit as st

from services.analyzer import analyze_text
from services.explanation_service import add_row_explanations
from views.history import save_history


TEXT_COLUMN_NAMES = [
    "text", "comment", "comments", "content", "review", "reviews",
    "message", "feedback", "description", "tweet", "post", "caption",
]


def _read_csv(uploaded_file):
    raw = uploaded_file.getvalue()

    if not raw:
        raise ValueError("The uploaded CSV is empty.")

    last_error = None

    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            df = pd.read_csv(
                io.BytesIO(raw),
                encoding=encoding,
                sep=None,
                engine="python",
                on_bad_lines="error",
            )

            if df.empty and len(df.columns) == 0:
                raise ValueError("No columns were detected.")

            return df

        except Exception as exc:
            last_error = exc

    raise ValueError(f"Could not read the CSV: {last_error}")


def _find_text_column(df):
    normalized = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for name in TEXT_COLUMN_NAMES:
        if name in normalized:
            return normalized[name]

    candidates = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    if not candidates:
        return None

    def score(column):
        sample = df[column].dropna().astype(str).head(100)

        if sample.empty:
            return 0

        return (sample.str.len() >= 8).mean()

    return max(candidates, key=score)


def _safe_float(value):
    try:
        number = float(value)
        if pd.notna(number):
            return max(0.0, min(1.0, number))
    except (TypeError, ValueError):
        pass

    return 0.0


def _metric_card(title, value, emoji):
    st.markdown(
        f"""
        <div class="csv-metric-card">
            <div class="csv-metric-icon">{emoji}</div>
            <div class="csv-metric-label">{html.escape(str(title))}</div>
            <div class="csv-metric-value">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _section(title, subtitle=None):
    st.markdown(
        f'<div class="csv-section-title">{html.escape(title)}</div>',
        unsafe_allow_html=True,
    )

    if subtitle:
        st.caption(subtitle)


def _add_styles():
    st.markdown(
        """
        <style>
        .csv-page-title {
            font-size: 32px;
            font-weight: 750;
            letter-spacing: -0.6px;
            margin-bottom: 5px;
        }

        .csv-page-subtitle {
            opacity: .75;
            margin-bottom: 22px;
            line-height: 1.6;
        }

        .csv-upload-card {
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(128,128,128,.25);
            background: var(--secondary-background-color);
            margin: 12px 0;
        }

        .csv-card-heading {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 7px;
        }

        .csv-muted {
            font-size: 13px;
            opacity: .75;
            line-height: 1.6;
        }

        .csv-section-title {
            font-size: 21px;
            font-weight: 720;
            margin: 26px 0 12px;
        }

        .csv-metric-card {
            padding: 16px;
            border-radius: 13px;
            border: 1px solid rgba(128,128,128,.25);
            background: var(--secondary-background-color);
            min-height: 105px;
            overflow-wrap: anywhere;
        }

        .csv-metric-icon {
            font-size: 22px;
            margin-bottom: 7px;
        }

        .csv-metric-label {
            opacity: .75;
            font-size: 12px;
        }

        .csv-metric-value {
            font-size: 25px;
            font-weight: 750;
            margin-top: 5px;
        }

        .csv-note {
            padding: 12px 15px;
            border-left: 3px solid #64748b;
            border-radius: 7px;
            background: var(--secondary-background-color);
            font-size: 13px;
            line-height: 1.7;
            margin: 12px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show():
    _add_styles()

    st.markdown(
        '<div class="csv-page-title">📂 CSV Dataset Analyzer</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="csv-page-subtitle">
            Analyze sentiment and emotions across your entire dataset.
            Explore charts, review explainable AI results, and download
            your complete analyzed CSV.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="csv-upload-card">
            <div class="csv-card-heading">📄 Upload your dataset</div>
            <div class="csv-muted">
                Upload a CSV containing comments, reviews, feedback,
                social media posts, or other text.
                Every data row will be considered for analysis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        key="csv_dataset_uploader",
    )

    if uploaded_file is None:
        st.info("Upload a CSV file to begin.")
        return

    try:
        with st.spinner("Reading CSV..."):
            original_df = _read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"Unable to read the CSV: {exc}")
        return

    if len(original_df.columns) == 0:
        st.error("No columns were found in the uploaded CSV.")
        return

    if original_df.empty:
        st.warning("The CSV contains no data rows.")
        return

    original_df.columns = [
        str(column).strip()
        for column in original_df.columns
    ]

    # ---------------------------------------------------------
    # Dataset overview
    # ---------------------------------------------------------
    _section("📊 Dataset overview")

    row_count = len(original_df)
    column_count = len(original_df.columns)
    missing_cells = int(original_df.isna().sum().sum())
    duplicate_rows = int(original_df.duplicated().sum())
    file_size_kb = len(uploaded_file.getvalue()) / 1024

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        _metric_card("Total rows", f"{row_count:,}", "📄")

    with c2:
        _metric_card("Columns", f"{column_count:,}", "▦")

    with c3:
        _metric_card("Missing cells", f"{missing_cells:,}", "⚠️")

    with c4:
        _metric_card("Duplicate rows", f"{duplicate_rows:,}", "♻️")

    st.caption(
        f"File: **{uploaded_file.name}** · "
        f"Size: **{file_size_kb:.1f} KB**"
    )

    with st.expander("Preview uploaded dataset"):
        st.dataframe(
            original_df.head(10),
            use_container_width=True,
            hide_index=True,
        )

    # ---------------------------------------------------------
    # Select text column
    # ---------------------------------------------------------
    _section("⚙️ Analysis settings")

    detected_column = _find_text_column(original_df)
    columns = list(original_df.columns)

    default_index = (
        columns.index(detected_column)
        if detected_column in columns
        else 0
    )

    text_column = st.selectbox(
        "Select the text column",
        options=columns,
        index=default_index,
    )

    skip_empty = st.checkbox(
        "Skip rows where the selected text is empty",
        value=True,
    )

    st.markdown(
        f"""
        <div class="csv-note">
            <strong>Full dataset mode enabled.</strong><br>
            All {row_count:,} rows will be considered.
            There is no 100-row limit or maximum-row selector.
            Empty text rows will be skipped only if the checkbox
            above is enabled.
        </div>
        """,
        unsafe_allow_html=True,
    )

    analyze_clicked = st.button(
        "🚀 Analyze ALL rows",
        type="primary",
        use_container_width=True,
    )

    if not analyze_clicked:
        return

    # ---------------------------------------------------------
    # IMPORTANT: Do not use head(100) or any row limit here.
    # ---------------------------------------------------------
    working_df = original_df.copy()

    working_df["text"] = (
        working_df[text_column]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    if skip_empty:
        empty_mask = working_df["text"].eq("")
        skipped_empty = int(empty_mask.sum())
        working_df = working_df.loc[~empty_mask].copy()
    else:
        skipped_empty = 0

    if working_df.empty:
        st.warning(
            "No non-empty text rows are available to analyze. "
            "Choose another text column or disable the empty-row filter."
        )
        return

    # ---------------------------------------------------------
    # Analyze ALL remaining rows
    # ---------------------------------------------------------
    records = []
    total = len(working_df)
    failed_records = 0

    _section("🧠 Processing dataset")

    progress_bar = st.progress(0)
    progress_text = st.empty()

    for position, (_, row) in enumerate(
        working_df.iterrows(),
        start=1,
    ):
        record = row.to_dict()
        text_value = row["text"]

        try:
            prediction = analyze_text(text_value)

            if not isinstance(prediction, dict):
                raise ValueError(
                    "The analyzer did not return a dictionary."
                )

            record["sentiment"] = str(
                prediction.get("sentiment", "unknown")
            ).strip().lower()

            record["sentiment_score"] = _safe_float(
                prediction.get("sentiment_score", 0.0)
            )

            record["emotion"] = str(
                prediction.get("emotion", "unknown")
            ).strip().lower()

            record["emotion_score"] = _safe_float(
                prediction.get("emotion_score", 0.0)
            )

            record["analysis_error"] = ""

        except Exception as exc:
            failed_records += 1

            record["sentiment"] = "unknown"
            record["sentiment_score"] = 0.0
            record["emotion"] = "unknown"
            record["emotion_score"] = 0.0
            record["analysis_error"] = str(exc)[:300]

        records.append(record)

        progress_bar.progress(position / total)
        progress_text.caption(
            f"Processed {position:,} of {total:,} usable rows"
        )

    progress_text.empty()
    progress_bar.empty()

    result_df = pd.DataFrame(records)

    # ---------------------------------------------------------
    # Explainable AI
    # ---------------------------------------------------------
    try:
        result_df = add_row_explanations(
            result_df,
            text_col="text",
            sentiment_col="sentiment",
            sentiment_score_col="sentiment_score",
            emotion_col="emotion",
            emotion_score_col="emotion_score",
        )
    except Exception as exc:
        st.warning(f"Some explanations could not be generated: {exc}")

        if "sentiment_explanation" not in result_df.columns:
            result_df["sentiment_explanation"] = (
                "Explanation unavailable."
            )

        if "evidence_phrases" not in result_df.columns:
            result_df["evidence_phrases"] = "Unavailable"

        if "emotion_explanation" not in result_df.columns:
            result_df["emotion_explanation"] = (
                "Explanation unavailable."
            )

    # ---------------------------------------------------------
    # Store results for other modules
    # ---------------------------------------------------------
    st.session_state.analysis_df = result_df
    st.session_state.csv_filename = uploaded_file.name

    st.success(
        f"Finished processing {len(result_df):,} rows."
    )

    if skipped_empty:
        st.info(
            f"{skipped_empty:,} empty row(s) were skipped."
        )

    if failed_records:
        st.warning(
            f"{failed_records:,} row(s) failed model analysis "
            "and are marked unknown. See analysis_error in the results."
        )

    # ---------------------------------------------------------
    # Calculate summary
    # ---------------------------------------------------------
    _section("📈 Analysis results")

    sentiments = (
        result_df["sentiment"]
        .fillna("unknown")
        .astype(str)
        .str.lower()
    )

    emotions = (
        result_df["emotion"]
        .fillna("unknown")
        .astype(str)
        .str.lower()
    )

    sentiment_counts = sentiments.value_counts()

    positive = int(sentiment_counts.get("positive", 0))
    neutral = int(sentiment_counts.get("neutral", 0))
    negative = int(sentiment_counts.get("negative", 0))
    unknown = int(sentiment_counts.get("unknown", 0))

    valid_sentiments = sentiments[
        sentiments.isin(["positive", "neutral", "negative"])
    ]

    valid_emotions = emotions[emotions != "unknown"]

    dominant_sentiment = (
        valid_sentiments.value_counts().idxmax()
        if not valid_sentiments.empty
        else "unknown"
    )

    dominant_emotion = (
        valid_emotions.value_counts().idxmax()
        if not valid_emotions.empty
        else "unknown"
    )

    sentiment_scores = pd.to_numeric(
        result_df["sentiment_score"],
        errors="coerce",
    )

    emotion_scores = pd.to_numeric(
        result_df["emotion_score"],
        errors="coerce",
    )

    valid_sentiment_scores = sentiment_scores[
        sentiments.isin(["positive", "neutral", "negative"])
    ]

    valid_emotion_scores = emotion_scores[
        emotions != "unknown"
    ]

    avg_sentiment_score = (
        float(valid_sentiment_scores.mean())
        if not valid_sentiment_scores.empty
        else 0.0
    )

    avg_emotion_score = (
        float(valid_emotion_scores.mean())
        if not valid_emotion_scores.empty
        else 0.0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        _metric_card("Positive", f"{positive:,}", "😊")

    with c2:
        _metric_card("Neutral", f"{neutral:,}", "😐")

    with c3:
        _metric_card("Negative", f"{negative:,}", "😟")

    with c4:
        _metric_card(
            "Average sentiment confidence",
            f"{avg_sentiment_score:.1%}",
            "🎯",
        )

    st.markdown(
        f"""
        <div class="csv-note">
            <strong>Dominant sentiment:</strong>
            {html.escape(dominant_sentiment.capitalize())}<br>
            <strong>Dominant emotion:</strong>
            {html.escape(dominant_emotion.capitalize())}<br>
            <strong>Average emotion confidence:</strong>
            {avg_emotion_score:.1%}<br>
            <strong>Rows in results:</strong> {len(result_df):,}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Charts
    # ---------------------------------------------------------
    _section("📊 Visualizations")

    left, right = st.columns(2)

    with left:
        st.markdown("**Sentiment distribution**")

        chart_sentiment = sentiments.value_counts().reindex(
            ["positive", "neutral", "negative", "unknown"],
            fill_value=0,
        )

        st.bar_chart(chart_sentiment)

    with right:
        st.markdown("**Emotion distribution**")

        emotion_distribution = valid_emotions.value_counts().head(10)

        if emotion_distribution.empty:
            st.info("No valid emotion predictions to display.")
        else:
            st.bar_chart(emotion_distribution)

    # ---------------------------------------------------------
    # XAI preview
    # ---------------------------------------------------------
    _section("🔎 Explainable AI results")

    xai_columns = [
        "text",
        "sentiment",
        "sentiment_score",
        "evidence_phrases",
        "sentiment_explanation",
        "emotion",
        "emotion_score",
        "emotion_explanation",
    ]

    xai_columns = [
        col for col in xai_columns
        if col in result_df.columns
    ]

    with st.expander("View explanations", expanded=True):
        st.dataframe(
            result_df[xai_columns].head(20),
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "These explanations use rule-based keyword clues. "
            "They are human-readable explanations, not a transcript "
            "of the model's internal reasoning."
        )

    # ---------------------------------------------------------
    # Complete results
    # ---------------------------------------------------------
    _section("🗂️ Complete analyzed dataset")

    st.caption(
        f"Displaying {len(result_df):,} analyzed records."
    )

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True,
    )

    # ---------------------------------------------------------
    # Download all results
    # ---------------------------------------------------------
    _section("⬇️ Download results")

    csv_data = result_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    base_name = uploaded_file.name.rsplit(".", 1)[0]

    st.download_button(
        "Download complete analyzed CSV",
        data=csv_data,
        file_name=f"{base_name}_analyzed.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
    )

    # ---------------------------------------------------------
    # Save analysis to History
    # ---------------------------------------------------------
    try:
        save_history(
            analysis_type="CSV",
            records_count=len(result_df),
            sentiment=dominant_sentiment.capitalize(),
            emotion=dominant_emotion.capitalize(),
            source_name=uploaded_file.name,
            details={
                "records": result_df.to_dict(orient="records"),
                "metadata": {
                    "filename": uploaded_file.name,
                    "text_column": str(text_column),
                    "uploaded_rows": int(len(original_df)),
                    "processed_rows": int(len(result_df)),
                    "skipped_empty_rows": int(skipped_empty),
                    "failed_records": int(failed_records),
                    "positive_records": positive,
                    "neutral_records": neutral,
                    "negative_records": negative,
                    "unknown_records": unknown,
                    "dominant_sentiment": dominant_sentiment,
                    "dominant_emotion": dominant_emotion,
                    "average_sentiment_confidence": avg_sentiment_score,
                    "average_emotion_confidence": avg_emotion_score,
                },
            },
        )

        st.success("Analysis saved to History.")

    except Exception as exc:
        st.warning(
            "The analysis completed, but History could not save the details."
        )

        with st.expander("History error details"):
            st.code(str(exc))


show_csv = show
