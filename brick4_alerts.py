
from pathlib import Path
from datetime import datetime
import py_compile
import re
import shutil

target = Path("views/dashboard.py")
source = target.read_text(encoding="utf-8")

marker = "# BRICK_4_SENTIMENT_ALERTS"

if marker in source:
    print("Brick 4 already exists. No changes made.")
    raise SystemExit(0)

# Insert after the existing Key Insights section and before
# the negative-comment investigation section.
anchor = "# BRICK_2A_NEGATIVE_COMMENT_REVIEW"

if anchor not in source:
    print(f"Could not find insertion anchor: {anchor}")
    print("No changes made.")
    raise SystemExit(1)

section = '''
    # BRICK_4_SENTIMENT_ALERTS
    section(
        "Sentiment alerts & recommended actions",
        "Set a threshold to identify when negative audience reactions "
        "need closer attention."
    )

    alert_threshold = st.slider(
        "Alert when negative sentiment reaches (%)",
        min_value=5,
        max_value=80,
        value=30,
        step=5,
        key="brick4_negative_alert_threshold",
    )

    alert_col1, alert_col2 = st.columns(2, gap="medium")

    with alert_col1:
        st.metric("Current negative sentiment", f"{negative_pct:.1f}%")

    with alert_col2:
        st.metric("Alert threshold", f"{alert_threshold}%")

    if total_records == 0:
        st.info("Run an analysis with records to generate sentiment alerts.")
    elif negative_pct >= alert_threshold:
        st.error(
            f"Attention needed: negative sentiment is {negative_pct:.1f}%, "
            f"which meets or exceeds your {alert_threshold}% threshold."
        )
    else:
        st.success(
            f"Negative sentiment is below your {alert_threshold}% threshold."
        )

    st.markdown("#### Recommended next steps")

    if negative_pct >= alert_threshold:
        st.markdown(
            "- Review the negative records below and identify recurring "
            "complaints or concerns.\\n"
            "- Group similar complaints into themes before deciding what "
            "action to take.\\n"
            "- Recheck sentiment after addressing the main concerns."
        )
    elif negative > 0:
        st.markdown(
            "- Review a sample of negative records for recurring issues.\\n"
            "- Monitor whether the negative share increases in your next "
            "analysis."
        )
    else:
        st.markdown(
            "- No negative records were detected in this dataset.\\n"
            "- Continue monitoring future results; this does not guarantee "
            "that all audience feedback is positive."
        )

    if "dashboard_emotion" in data.columns:
        valid_emotions = (
            data["dashboard_emotion"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        valid_emotions = valid_emotions[
            ~valid_emotions.str.lower().isin(
                ["", "nan", "none", "unknown"]
            )
        ]

        if not valid_emotions.empty:
            emotion_counts = valid_emotions.value_counts()
            leading_emotion = emotion_counts.index[0]
            st.info(
                f"Most frequent detected emotion: **{leading_emotion}** "
                f"({int(emotion_counts.iloc[0]):,} records). "
                "Use this as a signal to investigate, not as proof of "
                "the audience's actual feelings."
            )

'''

# Preserve the original file and validate the patched version first.
updated = source.replace(anchor, section + "    " + anchor, 1)

backup = target.with_name(
    f"dashboard.py.backup_brick4_{datetime.now():%Y%m%d_%H%M%S}"
)
temporary = target.with_suffix(".py.brick4tmp")

shutil.copy2(target, backup)
temporary.write_text(updated, encoding="utf-8")

try:
    py_compile.compile(str(temporary), doraise=True)
    target.write_text(updated, encoding="utf-8")
except Exception:
    temporary.unlink(missing_ok=True)
    print("Patch failed. The original dashboard was preserved.")
    raise
else:
    temporary.unlink(missing_ok=True)

print("Brick 4 installed successfully.")
print(f"Backup: {backup}")
