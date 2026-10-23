from pathlib import Path
from datetime import datetime
import py_compile
import sys

target = Path("app.py")
source = target.read_text()

if '"navigation_page"' in source or "'navigation_page'" in source:
    sys.exit("Navigation marker already exists. Stop and inspect app.py.")

start_token = '    page = st.radio(\n        "Navigation",'
start = source.find(start_token)

if start == -1:
    sys.exit("STOP: Could not find the existing sidebar radio. No app changes made.")

end_token = '\n    )'
end = source.find(end_token, start)

if end == -1:
    sys.exit("STOP: Could not find the end of the radio call. No app changes made.")

end += len(end_token)
old_block = source[start:end]

if '"📉 Dashboard"' not in old_block or '"📺 YouTube Analyzer"' not in old_block:
    sys.exit("STOP: The expected navigation options were not found. No app changes made.")

new_block = '''    page_options = [
        "🏠 Home",
        "📺 YouTube Analyzer",
        "📝 Text Analyzer",
        "📂 CSV Upload",
        "📊 Analytics",
        "📈 Trend Analyzer",
        "🤖 AI Assistant",
        "🧠 AI Insights",
        "📄 Reports",
        "🕒 History",
        "📉 Dashboard",
    ]

    if "navigation_page" in st.session_state:
        requested_page = st.session_state.pop("navigation_page")
        if requested_page in page_options:
            st.session_state["Navigation"] = requested_page

    page = st.radio(
        "Navigation",
        page_options,
        key="Navigation",
    )'''

updated = source[:start] + new_block + source[end:]

backup = target.with_name(
    f"app.py.brick6-backup-{datetime.now():%Y%m%d-%H%M%S}"
)
temporary = target.with_name("app.py.brick6-tmp")

try:
    backup.write_text(source)
    temporary.write_text(updated)
    py_compile.compile(str(temporary), doraise=True)
    target.write_text(updated)
    print("SUCCESS: Navigation connection installed.")
    print("Python syntax test: PASSED")
    print(f"Backup: {backup}")
except Exception as exc:
    print(f"FAILED: {exc}")
    print("Stop and send me the exact message.")
    sys.exit(1)
finally:
    if temporary.exists():
        temporary.unlink()
