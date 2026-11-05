from pathlib import Path
from datetime import datetime
import py_compile
import sys

target = Path("views/dashboard.py")
if not target.exists():
    sys.exit("STOP: views/dashboard.py not found.")

source = target.read_text()
marker = "# BRICK_7_EMOTION_FILTER"

if marker in source:
    sys.exit("Brick 7 marker already exists. No changes made.")

old = '''    filter_col1, filter_col2 = st.columns([2, 1])

    with filter_col1:
        search_text = st.text_input(
            "Search records",
            placeholder="Search comments, reviews, or text...",
            key="dashboard_record_search",
        )

    with filter_col2:
        sentiment_options = ["All"] + sorted(
            data["dashboard_sentiment"].dropna().unique().tolist()
        )

        selected_sentiment = st.selectbox(
            "Filter by sentiment",
            options=sentiment_options,
            key="dashboard_sentiment_filter",
        )
'''

new = '''    # BRICK_7_EMOTION_FILTER
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])

    with filter_col1:
        search_text = st.text_input(
            "Search records",
            placeholder="Search comments, reviews, or text...",
            key="dashboard_record_search",
        )

    with filter_col2:
        sentiment_options = ["All"] + sorted(
            data["dashboard_sentiment"].dropna().unique().tolist()
        )

        selected_sentiment = st.selectbox(
            "Filter by sentiment",
            options=sentiment_options,
            key="dashboard_sentiment_filter",
        )

    with filter_col3:
        if "dashboard_emotion" in data.columns:
            emotion_options = ["All"] + sorted(
                data["dashboard_emotion"].dropna().astype(str).unique().tolist()
            )
        else:
            emotion_options = ["All"]

        selected_emotion = st.selectbox(
            "Filter by emotion",
            options=emotion_options,
            key="dashboard_emotion_filter",
        )
'''

if source.count(old) != 1:
    sys.exit("STOP: The expected filter section was not found exactly once. No changes made.")

updated = source.replace(old, new, 1)

anchor = '''    if selected_sentiment != "All":
        filtered_data = filtered_data[
            filtered_data["dashboard_sentiment"] == selected_sentiment
        ]
'''

addition = anchor + '''
    if (
        selected_emotion != "All"
        and "dashboard_emotion" in filtered_data.columns
    ):
        filtered_data = filtered_data[
            filtered_data["dashboard_emotion"].astype(str) == selected_emotion
        ]
'''

if updated.count(anchor) != 1:
    sys.exit("STOP: The sentiment filtering block was not found exactly once. No changes made.")

updated = updated.replace(anchor, addition, 1)

backup = target.with_name(
    f"dashboard.py.brick7-backup-{datetime.now():%Y%m%d-%H%M%S}"
)
temporary = target.with_name("dashboard.py.brick7-tmp")

try:
    backup.write_text(source)
    temporary.write_text(updated)
    py_compile.compile(str(temporary), doraise=True)
    target.write_text(updated)
    print("SUCCESS: Emotion filter added.")
    print("Python syntax test: PASSED")
    print(f"Backup saved at: {backup}")
except Exception as exc:
    print(f"FAILED: {exc}")
    print("Stop and send me the error.")
    sys.exit(1)
finally:
    if temporary.exists():
        temporary.unlink()
