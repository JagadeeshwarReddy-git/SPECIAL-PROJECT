
import json
import math
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st


# ==========================================================
# CONFIGURATION
# ==========================================================

HISTORY_FILE = Path("analysis_history.json")
DETAILS_DIR = Path("analysis_details")
MAX_HISTORY = 50


# ==========================================================
# SHARED DATA
# ==========================================================

def get_shared_analysis_data():
    """Return the dataset currently shared across application pages."""

    for key in ("analysis_df", "universal_analysis_df", "df"):
        candidate = st.session_state.get(key)

        if isinstance(candidate, pd.DataFrame) and not candidate.empty:
            return candidate.copy()

    return None


# ==========================================================
# JSON UTILITIES
# ==========================================================

def _json_safe(value):
    """Convert Pandas, NumPy, and Python objects into JSON-safe values."""

    if value is None:
        return None

    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]

    if isinstance(value, pd.DataFrame):
        return _json_safe(value.to_dict(orient="records"))

    if isinstance(value, pd.Series):
        return _json_safe(value.to_dict())

    if isinstance(value, (datetime, pd.Timestamp)):
        return value.isoformat()

    if isinstance(value, Path):
        return str(value)

    if hasattr(value, "item") and callable(value.item):
        try:
            value = value.item()
        except (ValueError, TypeError):
            pass

    if value is None:
        return None

    if isinstance(value, float) and not math.isfinite(value):
        return None

    if not isinstance(value, (str, bytes, list, tuple, dict)):
        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            pass

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


# ==========================================================
# HISTORY STORAGE
# ==========================================================

def load_history():
    """Load saved history summaries."""

    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        return [
            item for item in data
            if isinstance(item, dict)
        ]

    except (json.JSONDecodeError, OSError):
        return []


def _write(history):
    """Save history summaries safely."""

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            _json_safe(history),
            file,
            indent=4,
            ensure_ascii=False,
            allow_nan=False,
        )


def _details_path(item_id):
    """Build a safe path for a saved analysis detail file."""

    safe_id = "".join(
        character
        for character in str(item_id)
        if character.isalnum() or character in ("-", "_")
    )

    if not safe_id:
        return None

    return DETAILS_DIR / f"{safe_id}.json"


def load_history_details(item):
    """Load detailed results associated with a history entry."""

    if not isinstance(item, dict):
        return None

    details_file = item.get("details_file")

    if not details_file:
        return None

    filename = Path(str(details_file)).name

    if filename != str(details_file):
        return None

    path = _details_path(Path(filename).stem)

    if path is None or not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return None


# ==========================================================
# SAVE ANALYSIS HISTORY
# ==========================================================

def save_history(
    analysis_type,
    records_count,
    sentiment,
    emotion,
    source_name="Analysis",
    details=None,
):
    """
    Save an analysis summary and optional detailed results.

    Existing calls to save_history() remain compatible.
    """

    history = load_history()
    now = datetime.now()
    item_id = now.strftime("%Y%m%d%H%M%S%f")

    try:
        record_count = max(0, int(records_count))
    except (TypeError, ValueError):
        record_count = 0

    item = {
        "id": item_id,
        "date": now.strftime("%d %b %Y, %I:%M %p"),
        "type": str(analysis_type),
        "source": str(source_name),
        "records": record_count,
        "sentiment": str(sentiment),
        "emotion": str(emotion),
    }

    if details is not None:
        try:
            DETAILS_DIR.mkdir(parents=True, exist_ok=True)

            detail_path = _details_path(item_id)
            safe_details = _json_safe(details)

            with detail_path.open("w", encoding="utf-8") as file:
                json.dump(
                    safe_details,
                    file,
                    indent=2,
                    ensure_ascii=False,
                    allow_nan=False,
                )

            item["details_file"] = detail_path.name
            item["details_available"] = True

        except (OSError, TypeError, ValueError) as error:
            st.warning(
                f"History summary saved, but detailed results "
                f"could not be saved: {error}"
            )

    history.insert(0, item)

    # Keep the most recent MAX_HISTORY entries.
    removed_items = history[MAX_HISTORY:]
    history = history[:MAX_HISTORY]

    _write(history)

    # Remove detail files for entries dropped by the history limit.
    for removed in removed_items:
        path = _details_path(removed.get("id", ""))

        if path and path.exists():
            try:
                path.unlink()
            except OSError:
                pass


# ==========================================================
# DELETE HISTORY
# ==========================================================

def delete_history_items(ids):
    """Delete selected history entries."""

    ids = {str(item_id) for item_id in ids}
    history = load_history()
    remaining = []

    for item in history:
        if str(item.get("id", "")) in ids:
            path = _details_path(item.get("id", ""))

            if path and path.exists():
                try:
                    path.unlink()
                except OSError:
                    pass
        else:
            remaining.append(item)

    _write(remaining)


def delete_history_item(item_id):
    """Delete one history entry."""

    delete_history_items({item_id})


def clear_history():
    """Clear all history summaries and their detail files."""

    for item in load_history():
        path = _details_path(item.get("id", ""))

        if path and path.exists():
            try:
                path.unlink()
            except OSError:
                pass

    _write([])


# ==========================================================
# DISPLAY HELPERS
# ==========================================================

def _type_icon(value):
    value = str(value).lower()

    if "youtube" in value:
        return "📺"

    if "text" in value:
        return "📝"

    if "csv" in value or "upload" in value:
        return "📂"

    return "📊"


def _sentiment_icon(value):
    value = str(value).lower()

    if value == "positive":
        return "😊"

    if value == "negative":
        return "😟"

    if value == "neutral":
        return "😐"

    return "🔎"


def _safe_int(value):
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _show_value(value):
    if value is None:
        return "Not available"

    if isinstance(value, (dict, list)):
        return json.dumps(
            _json_safe(value),
            indent=2,
            ensure_ascii=False,
        )

    return str(value)


# ==========================================================
# INDIVIDUAL ANALYSIS DETAILS
# ==========================================================

def _show_analysis_details(item):

    st.subheader(
        f"{_type_icon(item.get('type'))} Analysis Details"
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Records Analyzed",
        f"{_safe_int(item.get('records', 0)):,}",
    )

    col2.metric(
        "Analysis Type",
        str(item.get("type", "Unknown")),
    )

    st.markdown("### 📌 Analysis Summary")

    st.write("**Source:**", item.get("source", "Unknown"))
    st.write("**Date:**", item.get("date", "Unknown"))
    st.write("**Overall sentiment:**", item.get("sentiment", "Unknown"))
    st.write("**Dominant emotion:**", item.get("emotion", "Unknown"))

    details = load_history_details(item)

    if details is None:
        st.info(
            "Full details are not available for this entry. "
            "The summary may have been saved without detailed results, "
            "or the details file may be missing."
        )
        return

    if not isinstance(details, dict):
        st.json(details)
        return

    st.markdown("### 🔍 Saved Results")

    metadata = details.get("metadata", {})

    if isinstance(metadata, dict) and metadata:
        with st.expander(
            "Source and analysis information",
            expanded=True,
        ):
            for key, value in metadata.items():
                label = str(key).replace("_", " ").title()
                st.write(f"**{label}:**")
                st.write(_show_value(value))

    original_text = details.get("text")

    if original_text is not None:
        st.markdown("#### 📝 Original Text")

        st.text_area(
            "Text used for analysis",
            value=str(original_text),
            height=180,
            disabled=True,
            key=f"history_text_{item.get('id')}",
        )

    records = details.get("records")

    if isinstance(records, list) and records:
        results_df = pd.DataFrame(records)

        st.markdown(
            f"#### 📊 Individual Results ({len(results_df):,} records)"
        )

        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "⬇️ Download Detailed Results (CSV)",
            data=results_df.to_csv(index=False).encode("utf-8"),
            file_name=f"analysis_{item.get('id', 'details')}.csv",
            mime="text/csv",
            key=f"history_download_{item.get('id')}",
            use_container_width=True,
        )

    remaining_details = {
        key: value
        for key, value in details.items()
        if key not in {"metadata", "text", "records"}
    }

    if remaining_details:
        with st.expander("Additional Saved Information"):
            st.json(remaining_details)


# ==========================================================
# MAIN HISTORY PAGE
# ==========================================================

def show():

    st.markdown(
        """
        <style>
        .history-hero {
            padding: 24px 28px;
            border-radius: 18px;
            margin-bottom: 20px;
            color: white;
            background: linear-gradient(135deg, #667eea, #764ba2);
        }

        .history-hero h1 {
            color: white;
            margin: 0;
            font-size: 2rem;
        }

        .history-hero p {
            color: rgba(255,255,255,.9);
            margin: 7px 0 0;
        }

        .history-card {
            border: 1px solid rgba(128,128,128,.25);
            border-radius: 14px;
            padding: 16px;
            margin: 8px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="history-hero">
            <h1>🕒 Analysis History</h1>
            <p>Search previous analyses and review saved results.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history = load_history()

    # ------------------------------------------------------
    # OPEN ONE HISTORY ENTRY
    # ------------------------------------------------------

    detail_id = st.session_state.get("history_detail_id")

    if detail_id:
        selected_item = next(
            (
                item for item in history
                if str(item.get("id")) == str(detail_id)
            ),
            None,
        )

        if selected_item is None:
            st.session_state.pop("history_detail_id", None)
            st.warning("This history entry no longer exists.")
            st.rerun()

        if st.button("← Back to Analysis History"):
            st.session_state.pop("history_detail_id", None)
            st.rerun()

        _show_analysis_details(selected_item)
        return

    # ------------------------------------------------------
    # CURRENT DATASET PREVIEW
    # ------------------------------------------------------

    with st.expander("📂 Current Shared Dataset", expanded=False):

        current_df = get_shared_analysis_data()

        if current_df is None:
            st.info(
                "No current dataset is available in this session. "
                "Upload a CSV or run an analysis first."
            )
        else:
            col1, col2 = st.columns(2)

            col1.metric("Current Records", f"{len(current_df):,}")
            col2.metric("Columns", f"{len(current_df.columns):,}")

            st.dataframe(
                current_df.head(10),
                use_container_width=True,
                hide_index=True,
            )

    # ------------------------------------------------------
    # EMPTY STATE
    # ------------------------------------------------------

    if not history:
        st.info(
            "🗂️ No saved analysis history yet. "
            "Run an analysis that calls save_history() to create an entry."
        )
        return

    # ------------------------------------------------------
    # OVERVIEW
    # ------------------------------------------------------

    total_records = sum(
        _safe_int(item.get("records", 0))
        for item in history
    )

    positive_analyses = sum(
        str(item.get("sentiment", "")).strip().lower() == "positive"
        for item in history
    )

    analysis_types = len(
        set(str(item.get("type", "Analysis")) for item in history)
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📚 Saved Analyses", len(history))
    col2.metric("📊 Total Records", f"{total_records:,}")
    col3.metric("😊 Positive Analyses", positive_analyses)
    col4.metric("📂 Analysis Types", analysis_types)

    # ------------------------------------------------------
    # SEARCH AND FILTERS
    # ------------------------------------------------------

    st.subheader("🔎 Find an Analysis")

    f1, f2, f3 = st.columns([1.5, 1, 1])

    with f1:
        search = st.text_input(
            "Search",
            placeholder="Source, type, sentiment, or emotion...",
            key="history_search",
        )

    available_types = sorted(
        set(str(item.get("type", "Analysis")) for item in history)
    )

    with f2:
        selected_type = st.selectbox(
            "Analysis Type",
            ["All"] + available_types,
            key="history_type_filter",
        )

    with f3:
        selected_sentiment = st.selectbox(
            "Sentiment",
            ["All", "Positive", "Neutral", "Negative"],
            key="history_sentiment_filter",
        )

    filtered = []

    for item in history:
        analysis_type = str(item.get("type", "Analysis"))
        sentiment = str(item.get("sentiment", ""))
        source = str(item.get("source", ""))
        emotion = str(item.get("emotion", ""))
        date = str(item.get("date", ""))

        searchable_text = (
            f"{analysis_type} {sentiment} {source} {emotion} {date}"
        ).lower()

        if search.strip().lower() not in searchable_text:
            continue

        if selected_type != "All" and analysis_type != selected_type:
            continue

        if (
            selected_sentiment != "All"
            and sentiment.lower() != selected_sentiment.lower()
        ):
            continue

        filtered.append(item)

    st.subheader("📋 Saved Analyses")

    st.caption(
        f"Showing {len(filtered)} of {len(history)} saved analyses."
    )

    if not filtered:
        st.warning("No history entries match your filters.")
        return

    # ------------------------------------------------------
    # HISTORY CARDS
    # ------------------------------------------------------

    select_all = st.checkbox(
        "Select all visible entries",
        key="history_select_all",
    )

    selected_ids = []

    for index, item in enumerate(filtered):
        item_id = str(item.get("id", index))
        analysis_type = str(item.get("type", "Analysis"))
        sentiment = str(item.get("sentiment", "Unknown"))
        source = str(item.get("source", "Unknown source"))
        emotion = str(item.get("emotion", "Unknown"))

        with st.container(border=True):

            checkbox_col, details_col = st.columns([0.08, 0.92])

            with checkbox_col:
                checked = st.checkbox(
                    "Select",
                    value=select_all,
                    key=f"history_select_{item_id}",
                    label_visibility="collapsed",
                )

                if checked:
                    selected_ids.append(item_id)

            with details_col:
                st.markdown(
                    f"**{_type_icon(analysis_type)} {analysis_type}**"
                )

                st.caption(item.get("date", "Date unavailable"))

                st.write(f"**Source:** {source}")

                a, b, c = st.columns(3)

                a.metric(
                    "Records",
                    f"{_safe_int(item.get('records', 0)):,}",
                )

                b.metric(
                    "Sentiment",
                    f"{_sentiment_icon(sentiment)} {sentiment}",
                )

                c.metric("Emotion", emotion)

                if item.get("details_available"):
                    st.caption("Detailed results saved")

                if st.button(
                    "🔍 View Details",
                    key=f"history_view_{item_id}",
                    use_container_width=True,
                ):
                    st.session_state["history_detail_id"] = item_id
                    st.rerun()

    # ------------------------------------------------------
    # DELETE ACTIONS
    # ------------------------------------------------------

    st.divider()

    left, right = st.columns(2)

    with left:
        if st.button(
            f"🗑️ Delete Selected ({len(selected_ids)})",
            disabled=not selected_ids,
            use_container_width=True,
        ):
            delete_history_items(selected_ids)
            st.session_state.pop("history_select_all", None)
            st.rerun()

    with right:
        if st.button(
            "🧹 Clear Entire History",
            use_container_width=True,
        ):
            st.session_state["confirm_clear_history"] = True

    if st.session_state.get("confirm_clear_history", False):

        st.warning(
            "This permanently deletes saved history summaries and "
            "their associated detail files."
        )

        confirm_col, cancel_col = st.columns(2)

        with confirm_col:
            if st.button(
                "Yes, Clear History",
                use_container_width=True,
            ):
                clear_history()
                st.session_state["confirm_clear_history"] = False
                st.session_state.pop("history_detail_id", None)
                st.session_state.pop("history_select_all", None)
                st.rerun()

        with cancel_col:
            if st.button(
                "Cancel",
                use_container_width=True,
            ):
                st.session_state["confirm_clear_history"] = False
                st.rerun()

    # ------------------------------------------------------
    # HISTORY DISTRIBUTION
    # ------------------------------------------------------

    st.divider()
    st.subheader("📈 Analysis Type Distribution")

    distribution = (
        pd.Series([
            str(item.get("type", "Analysis"))
            for item in filtered
        ])
        .value_counts()
        .rename_axis("Analysis Type")
        .to_frame("Count")
    )

    st.bar_chart(distribution)

    # ------------------------------------------------------
    # EXPORT FILTERED HISTORY
    # ------------------------------------------------------

    st.subheader("⬇️ Export History")

    export_df = pd.DataFrame([
        {
            "Date": item.get("date", ""),
            "Analysis Type": item.get("type", ""),
            "Source": item.get("source", ""),
            "Records": item.get("records", 0),
            "Sentiment": item.get("sentiment", ""),
            "Emotion": item.get("emotion", ""),
            "Details Available": item.get("details_available", False),
        }
        for item in filtered
    ])

    st.download_button(
        "Download Filtered History (CSV)",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="analysis_history.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ==========================================================
# COMPATIBILITY ALIAS
# ==========================================================

show_history = show
