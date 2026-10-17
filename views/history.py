
import json
import math
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

HISTORY_FILE = Path("analysis_history.json")
DETAILS_DIR = Path("analysis_details")
MAX_HISTORY = 50


# --------------------------------------------------
# HISTORY STORAGE
# --------------------------------------------------

def load_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def _write(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


def _json_safe(value):
    """Convert common Python, Pandas and NumPy values to JSON-safe values."""

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

    if hasattr(value, "item") and callable(value.item):
        try:
            value = value.item()
        except (ValueError, TypeError):
            pass

    if value is None:
        return None

    if isinstance(value, float) and not math.isfinite(value):
        return None

    if pd.isna(value) if not isinstance(value, (str, bytes, list, tuple, dict)) else False:
        return None

    if isinstance(value, (datetime, pd.Timestamp)):
        return value.isoformat()

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def _details_path(item_id):
    """Build a safe details-file path from a history ID."""

    safe_id = "".join(
        character for character in str(item_id)
        if character.isalnum() or character in ("-", "_")
    )

    if not safe_id:
        return None

    return DETAILS_DIR / f"{safe_id}.json"


def load_history_details(item):
    """Load the full details for one history entry, if they were saved."""

    if not isinstance(item, dict):
        return None

    details_file = item.get("details_file")

    if not details_file:
        return None

    # Only accept filenames stored directly inside our details directory.
    filename = Path(str(details_file)).name
    if filename != str(details_file):
        return None

    path = _details_path(Path(filename).stem)

    if path is None or not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return None


def save_history(
    analysis_type,
    records_count,
    sentiment,
    emotion,
    source_name="Analysis",
    details=None,
):
    """
    Save summary information and, optionally, the full analysis details.

    Existing calls to save_history() still work because details is optional.
    """

    history = load_history()
    now = datetime.now()

    item_id = now.strftime("%Y%m%d%H%M%S%f")

    item = {
        "id": item_id,
        "date": now.strftime("%d %b %Y, %I:%M %p"),
        "type": str(analysis_type),
        "source": str(source_name),
        "records": int(records_count),
        "sentiment": str(sentiment),
        "emotion": str(emotion),
    }

    if details is not None:
        try:
            DETAILS_DIR.mkdir(parents=True, exist_ok=True)

            detail_path = _details_path(item_id)
            safe_details = _json_safe(details)

            with open(detail_path, "w", encoding="utf-8") as file:
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
            st.warning(f"Analysis summary saved, but detailed results could not be saved: {error}")

    history.insert(0, item)

    # Keep only the most recent MAX_HISTORY entries.
    removed_items = history[MAX_HISTORY:]
    history = history[:MAX_HISTORY]
    _write(history)

    # Remove detail files belonging to entries dropped by the history limit.
    for removed in removed_items:
        path = _details_path(removed.get("id", ""))
        if path and path.exists():
            try:
                path.unlink()
            except OSError:
                pass


def delete_history_items(ids):
    ids = {str(item_id) for item_id in ids}
    history = load_history()
    remaining = []

    for item in history:
        if str(item.get("id")) in ids:
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
    delete_history_items({item_id})


def clear_history():
    for item in load_history():
        path = _details_path(item.get("id", ""))
        if path and path.exists():
            try:
                path.unlink()
            except OSError:
                pass

    _write([])


# --------------------------------------------------
# DISPLAY HELPERS
# --------------------------------------------------

def _type_icon(value):
    return {
        "youtube": "📺",
        "text": "📝",
        "csv": "📂",
    }.get(str(value).lower(), "📊")


def _sentiment_icon(value):
    return {
        "positive": "😊",
        "negative": "😟",
        "neutral": "😐",
    }.get(str(value).lower(), "🔎")


def _show_value(value):
    if value is None:
        return "Not available"

    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, ensure_ascii=False)

    return str(value)


# --------------------------------------------------
# INDIVIDUAL ANALYSIS DETAILS
# --------------------------------------------------

def _show_analysis_details(item):
    st.markdown(f"## {_type_icon(item.get('type'))} Analysis Details")

    left, right = st.columns(2)

    with left:
        st.metric("Records Analyzed", f"{int(item.get('records', 0)):,}")

    with right:
        st.metric("Analysis Type", str(item.get("type", "Unknown")))

    st.markdown("### 📌 Analysis Summary")

    st.write("**Source:**", item.get("source", "Unknown"))
    st.write("**Date:**", item.get("date", "Unknown"))
    st.write("**Overall sentiment:**", item.get("sentiment", "Unknown"))
    st.write("**Dominant emotion:**", item.get("emotion", "Unknown"))

    details = load_history_details(item)

    if details is None:
        st.info(
            "Full details are not available for this entry. "
            "This analysis was saved without a detailed-results file, "
            "or its details file is missing. Older history entries cannot "
            "recover results that were never saved."
        )
        return

    if not isinstance(details, dict):
        st.warning("The saved details have an unexpected format.")
        st.json(details)
        return

    st.markdown("### 🔍 Saved Results")

    # Display extra metadata separately from the full result records.
    metadata = details.get("metadata", {})

    if isinstance(metadata, dict) and metadata:
        with st.expander("Source and analysis information", expanded=True):
            for key, value in metadata.items():
                st.write(f"**{str(key).replace('_', ' ').title()}:**")
                st.write(_show_value(value))

    # Show the original text when it was saved.
    original_text = details.get("text")

    if original_text is not None:
        st.markdown("#### 📝 Original Text")
        st.text_area(
            "Text used for analysis",
            value=str(original_text),
            height=180,
            disabled=True,
            key=f"history_original_text_{item.get('id')}",
        )

    # Show individual results as a table if the analyzer saved them.
    records = details.get("records")

    if isinstance(records, list) and records:
        st.markdown(f"#### 📊 Individual Results ({len(records):,} records)")

        results_df = pd.DataFrame(records)

        if not results_df.empty:
            st.dataframe(
                results_df,
                use_container_width=True,
                hide_index=True,
            )

            csv_data = results_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "⬇️ Download Detailed Results (CSV)",
                data=csv_data,
                file_name=f"analysis_{item.get('id', 'details')}.csv",
                mime="text/csv",
                key=f"history_download_{item.get('id')}",
                use_container_width=True,
            )

    # Display any remaining details not already rendered.
    remaining_details = {
        key: value
        for key, value in details.items()
        if key not in {"metadata", "text", "records"}
    }

    if remaining_details:
        with st.expander("Additional saved information"):
            st.json(remaining_details)

    if not original_text and not records and not metadata and not remaining_details:
        st.info("The detailed-results file is empty.")


# --------------------------------------------------
# MAIN HISTORY PAGE
# --------------------------------------------------

def show():
    st.markdown("""
    <style>
    .history-hero {
        padding:24px 28px;
        border-radius:20px;
        margin-bottom:22px;
        color:white;
        background:linear-gradient(135deg,#667eea,#764ba2,#f093fb);
    }
    .history-hero h1 {
        color:white;
        margin:0;
        font-size:2.15rem;
    }
    .history-hero p {
        color:rgba(255,255,255,.9);
        margin:7px 0 0;
    }
    .hcard {
        border:1px solid rgba(128,128,128,.22);
        border-radius:16px;
        padding:17px;
        margin:7px 0;
        background:rgba(128,128,128,.035);
    }
    .htop {
        display:flex;
        justify-content:space-between;
        gap:15px;
        flex-wrap:wrap;
    }
    .hsource {
        font-size:15px;
        font-weight:650;
        margin:10px 0 14px;
        word-break:break-word;
    }
    .hdetails {
        display:flex;
        gap:30px;
        flex-wrap:wrap;
    }
    .hdetail span {
        display:block;
        font-size:11px;
        opacity:.6;
    }
    .hdetail strong {
        font-size:13px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="history-hero">
        <h1>🕒 Analysis History</h1>
        <p>Search previous analyses and open saved results in detail.</p>
    </div>
    """, unsafe_allow_html=True)

    # Keep the selected detail page open across Streamlit reruns.
    history = load_history()
    detail_id = st.session_state.get("history_detail_id")

    if detail_id:
        selected_item = next(
            (x for x in history if str(x.get("id")) == str(detail_id)),
            None,
        )

        if selected_item is None:
            st.session_state.pop("history_detail_id", None)
            st.warning("This history entry no longer exists.")
            st.rerun()

        if st.button("← Back to Analysis History", use_container_width=False):
            st.session_state.pop("history_detail_id", None)
            st.rerun()

        _show_analysis_details(selected_item)
        return

    if not history:
        st.info("🗂️ No analysis history yet. Analyze YouTube, Text or CSV data first.")
        return

    # Summary cards.
    total_records = sum(int(x.get("records", 0)) for x in history)
    positive = sum(
        str(x.get("sentiment", "")).lower() == "positive"
        for x in history
    )
    types_count = len(set(str(x.get("type", "Analysis")) for x in history))

    a, b, c, d = st.columns(4)
    a.metric("📚 Saved Analyses", len(history))
    b.metric("📊 Total Records", f"{total_records:,}")
    c.metric("😊 Positive Analyses", positive)
    d.metric("📂 Analysis Types", types_count)

    st.markdown("### 🔎 Find an Analysis")

    f1, f2, f3 = st.columns([1.5, 1, 1])

    with f1:
        search = st.text_input(
            "Search",
            placeholder="Source, type, sentiment, emotion...",
        )

    with f2:
        types_list = ["All"] + sorted(
            set(str(x.get("type", "Analysis")) for x in history)
        )
        selected_type = st.selectbox("Type", types_list)

    with f3:
        selected_sentiment = st.selectbox(
            "Sentiment",
            ["All", "Positive", "Neutral", "Negative"],
        )

    filtered = []

    for item in history:
        typ = str(item.get("type", "Analysis"))
        sentiment = str(item.get("sentiment", ""))

        searchable = " ".join([
            typ,
            str(item.get("source", "")),
            sentiment,
            str(item.get("emotion", "")),
            str(item.get("date", "")),
        ]).lower()

        if search.strip() and search.strip().lower() not in searchable:
            continue

        if selected_type != "All" and typ != selected_type:
            continue

        if (
            selected_sentiment != "All"
            and sentiment.lower() != selected_sentiment.lower()
        ):
            continue

        filtered.append(item)

    st.markdown("### 📋 Saved Analyses")
    st.caption(f"Showing {len(filtered)} of {len(history)} saved analyses.")

    if not filtered:
        st.warning("No history items match your filters.")
        return

    select_all = st.checkbox("☑️ Select all visible items")
    selected_ids = []

    for i, item in enumerate(filtered):
        item_id = str(item.get("id", i))
        typ = str(item.get("type", "Analysis"))
        sentiment = str(item.get("sentiment", "Unknown"))
        source = str(item.get("source", "Unknown source"))

        check_col, card_col = st.columns([0.06, 0.94])

        with check_col:
            checked = st.checkbox(
                "",
                value=select_all,
                key=f"history_select_{item_id}",
            )

            if checked:
                selected_ids.append(item_id)

        with card_col:
            st.markdown(f"""
            <div class="hcard">
                <div class="htop">
                    <div><b>{_type_icon(typ)} {typ}</b></div>
                    <div>🕒 {item.get("date", "")}</div>
                </div>
                <div class="hsource">{source}</div>
                <div class="hdetails">
                    <div class="hdetail">
                        <span>Records</span>
                        <strong>{int(item.get("records", 0)):,}</strong>
                    </div>
                    <div class="hdetail">
                        <span>Sentiment</span>
                        <strong>{_sentiment_icon(sentiment)} {sentiment}</strong>
                    </div>
                    <div class="hdetail">
                        <span>Emotion</span>
                        <strong>🎭 {item.get("emotion", "Unknown")}</strong>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(
                "🔍 View Details",
                key=f"history_view_{item_id}",
                use_container_width=True,
            ):
                st.session_state.history_detail_id = item_id
                st.rerun()

    st.divider()

    x, y = st.columns(2)

    with x:
        if st.button(
            f"🗑️ Delete Selected ({len(selected_ids)})",
            disabled=not selected_ids,
            use_container_width=True,
        ):
            delete_history_items(selected_ids)
            st.rerun()

    with y:
        if st.button(
            "🧹 Clear Entire History",
            use_container_width=True,
        ):
            st.session_state.confirm_clear_history = True

    if st.session_state.get("confirm_clear_history", False):
        st.warning("⚠️ This permanently deletes all saved history and detail files.")

        p, q = st.columns(2)

        with p:
            if st.button("Yes, Clear Everything", use_container_width=True):
                clear_history()
                st.session_state.confirm_clear_history = False
                st.session_state.pop("history_detail_id", None)
                st.rerun()

        with q:
            if st.button("Cancel", use_container_width=True):
                st.session_state.confirm_clear_history = False
                st.rerun()

    st.markdown("### 📊 History Distribution")

    distribution = (
        pd.Series([str(x.get("type", "Analysis")) for x in history])
        .value_counts()
        .rename_axis("Analysis Type")
        .to_frame("Count")
    )

    st.bar_chart(distribution, use_container_width=True)


show_history = show
