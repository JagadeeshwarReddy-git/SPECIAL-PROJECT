
from pathlib import Path
import py_compile
import re
import shutil
from datetime import datetime

target = Path("views/dashboard.py")
source = target.read_text(encoding="utf-8")

marker = "# BRICK_3_SENTIMENT_CONFIDENCE"

if marker in source:
    print("Brick 3 is already installed. No changes made.")
    raise SystemExit(0)

# Insert before the existing model evaluation section.
match = re.search(r"(?m)^[ \t]*# MODEL EVALUATION\b", source)

if not match:
    print("Could not find '# MODEL EVALUATION'. No changes made.")
    raise SystemExit(1)

section = '''
    # BRICK_3_SENTIMENT_CONFIDENCE
    st.markdown("### 🎯 Sentiment Confidence Analysis")
    st.caption(
        "Confidence indicates how strongly the model supports a prediction; "
        "it does not guarantee that the prediction is correct."
    )

    confidence_source = data.copy()

    if "sentiment_score" not in confidence_source.columns:
        st.info(
            "No sentiment_score field is available for this dataset. "
            "Run an analysis that provides confidence scores to use this section."
        )
    else:
        confidence_source["confidence_value"] = pd.to_numeric(
            confidence_source["sentiment_score"], errors="coerce"
        )

        confidence_source = confidence_source[
            confidence_source["confidence_value"].notna()
            & confidence_source["dashboard_sentiment"].isin(
                ["Positive", "Neutral", "Negative"]
            )
        ].copy()

        if confidence_source.empty:
            st.info("No valid sentiment confidence scores are available yet.")
        else:
            # Support either 0–1 probabilities or 0–100 percentages.
            score_max = float(confidence_source["confidence_value"].max())
            if score_max > 1 and score_max <= 100:
                confidence_source["confidence_pct"] = (
                    confidence_source["confidence_value"].clip(0, 100)
                )
            else:
                confidence_source["confidence_pct"] = (
                    confidence_source["confidence_value"].clip(0, 1) * 100
                )

            threshold = st.slider(
                "Low-confidence review threshold (%)",
                min_value=10,
                max_value=90,
                value=60,
                step=5,
                key="brick3_confidence_threshold",
            )

            average_confidence = float(
                confidence_source["confidence_pct"].mean()
            )
            low_confidence = confidence_source[
                confidence_source["confidence_pct"] < threshold
            ]

            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric(
                "Average confidence", f"{average_confidence:.1f}%"
            )
            metric_col2.metric(
                "Predictions reviewed", f"{len(confidence_source):,}"
            )
            metric_col3.metric(
                f"Below {threshold}% threshold", f"{len(low_confidence):,}"
            )

            confidence_chart = px.histogram(
                confidence_source,
                x="confidence_pct",
                nbins=10,
                title="Distribution of sentiment confidence",
                labels={"confidence_pct": "Confidence (%)"},
            )
            confidence_chart.update_layout(
                xaxis_title="Confidence (%)",
                yaxis_title="Number of records",
                bargap=0.08,
            )
            st.plotly_chart(
                confidence_chart,
                use_container_width=True,
                key="brick3_confidence_histogram",
            )

            if not low_confidence.empty:
                st.markdown("#### Records needing review")
                text_column = next(
                    (
                        column for column in
                        ["text", "comment", "comments", "content",
                         "review", "message"]
                        if column in low_confidence.columns
                    ),
                    None,
                )

                display_columns = []
                if text_column:
                    display_columns.append(text_column)
                display_columns.extend(
                    ["dashboard_sentiment", "confidence_pct"]
                )

                review_table = low_confidence[display_columns].copy()
                review_table = review_table.rename(
                    columns={
                        "dashboard_sentiment": "Predicted sentiment",
                        "confidence_pct": "Confidence (%)",
                    }
                )
                review_table["Confidence (%)"] = review_table[
                    "Confidence (%)"
                ].round(1)

                st.dataframe(
                    review_table,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.success(
                    "No valid predictions fall below the selected threshold."
                )

'''

# Match the indentation of the dashboard's existing section.
updated = source[:match.start()] + section + source[match.start():]

backup = target.with_name(
    f"dashboard.py.backup_brick3_{datetime.now():%Y%m%d_%H%M%S}"
)
shutil.copy2(target, backup)

# Write to a temporary file, compile it, and only then replace the target.
temporary = target.with_suffix(".py.brick3tmp")
temporary.write_text(updated, encoding="utf-8")

try:
    py_compile.compile(str(temporary), doraise=True)
    target.write_text(updated, encoding="utf-8")
    print("Brick 3 installed successfully.")
    print(f"Backup saved as: {backup}")
except Exception:
    temporary.unlink(missing_ok=True)
    print("Installation failed. The original dashboard was not replaced.")
    raise
else:
    temporary.unlink(missing_ok=True)
