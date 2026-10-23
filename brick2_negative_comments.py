
from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(__file__).resolve().parent
DASHBOARD = ROOT / "views" / "dashboard.py"

MARKER = "# BRICK_2A_NEGATIVE_COMMENT_REVIEW"
ANCHOR = "    # MODEL EVALUATION"

ADDITION = '''
    # BRICK_2A_NEGATIVE_COMMENT_REVIEW
    # ------------------------------------------------------
    # NEGATIVE COMMENT REVIEW
    # ------------------------------------------------------

    section(
        "Comments to investigate",
        "Review records classified as negative by the current analysis."
    )

    negative_data = data[
        data["dashboard_sentiment"] == "Negative"
    ].copy()

    comment_column = next(
        (
            column for column in [
                "text", "comment", "comments", "content",
                "review", "message"
            ]
            if column in negative_data.columns
        ),
        None,
    )

    review_col1, review_col2 = st.columns(2)

    with review_col1:
        st.metric("Negative records", f"{len(negative_data):,}")

    with review_col2:
        negative_share = (
            len(negative_data) / total_records * 100
            if total_records else 0
        )
        st.metric("Share of all records", f"{negative_share:.1f}%")

    if negative_data.empty:
        st.success(
            "No records were classified as negative in this analysis."
        )
    elif comment_column is None:
        st.warning(
            "Negative records exist, but no recognized text column "
            "was found to display their content."
        )
        st.dataframe(
            negative_data.head(100),
            use_container_width=True,
            hide_index=True,
        )
    else:
        review_columns = [comment_column, "dashboard_sentiment"]

        if "dashboard_emotion" in negative_data.columns:
            review_columns.append("dashboard_emotion")

        if "sentiment_score" in negative_data.columns:
            review_columns.append("sentiment_score")

        review_data = negative_data[review_columns].copy()
        review_data = review_data.rename(
            columns={
                comment_column: "Comment / Content",
                "dashboard_sentiment": "Sentiment",
                "dashboard_emotion": "Emotion",
                "sentiment_score": "Sentiment Score",
            }
        )

        st.dataframe(
            review_data.head(100),
            use_container_width=True,
            hide_index=True,
        )

        if len(review_data) > 100:
            st.caption(
                "Showing the first 100 negative records. "
                "The count above includes all negative records."
            )

'''

def main():
    if not (ROOT / "app.py").exists():
        raise SystemExit("ERROR: Run this script inside SP PROJECT.")

    if not DASHBOARD.exists():
        raise SystemExit("ERROR: views/dashboard.py not found.")

    source = DASHBOARD.read_text(encoding="utf-8")

    if MARKER in source:
        raise SystemExit("Brick 2A is already installed; no changes made.")

    if source.count(ANCHOR) != 1:
        raise SystemExit(
            "STOP: Expected insertion point was not found exactly once. "
            "No changes made."
        )

    updated = source.replace(ANCHOR, ADDITION + ANCHOR, 1)

    # Verify Python syntax before changing the original file.
    compile(updated, str(DASHBOARD), "exec")

    backup = DASHBOARD.with_name(
        f"dashboard.py.backup-{datetime.now():%Y%m%d-%H%M%S}"
    )
    shutil.copy2(DASHBOARD, backup)
    DASHBOARD.write_text(updated, encoding="utf-8")

    print("SUCCESS: Negative comment review section added.")
    print(f"Backup saved as: {backup.name}")
    print("Next: run the syntax check.")

if __name__ == "__main__":
    main()
