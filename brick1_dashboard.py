
from pathlib import Path
import re
import shutil
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DASHBOARD = ROOT / "views" / "dashboard.py"
MARKER = "# BRICK_1_UNIFIED_PLATFORM_OVERVIEW"

def main():
    if not (ROOT / "app.py").exists():
        raise SystemExit("ERROR: Run this script inside SP PROJECT.")

    if not DASHBOARD.exists():
        raise SystemExit("ERROR: views/dashboard.py was not found.")

    source = DASHBOARD.read_text(encoding="utf-8")

    if MARKER in source:
        raise SystemExit("Brick 1 is already installed.")

    # Locate the exact dashboard entry point.
    pattern = re.compile(
        r"(?m)^def show\(\):\s*\n[ \t]+apply_dashboard_styles\(\)[ \t]*$"
    )
    match = pattern.search(source)

    if not match:
        raise SystemExit(
            "STOP: Could not locate the expected dashboard entry point. "
            "Original file was not changed."
        )

    addition = '''
# BRICK_1_UNIFIED_PLATFORM_OVERVIEW
def render_platform_overview():
    """Render a unified overview of platform integration status."""
    import streamlit as st

    platforms = [
        ("YouTube", "Available", "Existing project integration"),
        ("Text Analysis", "Available", "Analyze text"),
        ("CSV Upload", "Available", "Analyze uploaded datasets"),
        ("Instagram", "Planned", "Authorized API integration required"),
        ("Facebook", "Planned", "Authorized API integration required"),
        ("X", "Planned", "Authorized API integration required"),
        ("Reddit", "Planned", "API integration required"),
        ("LinkedIn", "Planned", "Authorized API integration required"),
        ("TikTok", "Planned", "Authorized API integration required"),
    ]

    st.markdown("---")
    st.markdown("# Social Media Command Center")
    st.caption(
        "A unified overview of current analysis tools and future integrations."
    )

    available = sum(status == "Available" for _, status, _ in platforms)
    metrics = st.columns(3)
    metrics[0].metric("Platforms listed", len(platforms))
    metrics[1].metric("Available tools", available)
    metrics[2].metric("Planned integrations", len(platforms) - available)

    st.markdown("## Explore platforms")

    for start in range(0, len(platforms), 3):
        columns = st.columns(3)
        for column, (name, status, description) in zip(
            columns, platforms[start:start + 3]
        ):
            with column:
                with st.container(border=True):
                    st.markdown(f"### {name}")
                    if status == "Available":
                        st.success(status)
                    else:
                        st.info(status)
                    st.caption(description)

    st.markdown("---")

'''

    # Insert the new function and call it from the existing show().
    insertion_point = match.start()
    updated = source[:insertion_point] + addition + source[insertion_point:]

    call_pattern = re.compile(
        r"(?m)^def show\(\):\n([ \t]+apply_dashboard_styles\(\))"
    )
    updated, count = call_pattern.subn(
        lambda m: m.group(0) + "\n    render_platform_overview()",
        updated,
        count=1,
    )

    if count != 1 or updated == source:
        raise SystemExit("STOP: Verification failed; original file unchanged.")

    # Compile in memory before writing.
    compile(updated, str(DASHBOARD), "exec")

    backup = DASHBOARD.with_name(
        f"dashboard.py.backup-{datetime.now():%Y%m%d-%H%M%S}"
    )
    shutil.copy2(DASHBOARD, backup)
    DASHBOARD.write_text(updated, encoding="utf-8")

    print("SUCCESS: Brick 1 has been applied.")
    print(f"Backup: {backup.name}")
    print("Next: run python -m py_compile views/dashboard.py")

if __name__ == "__main__":
    main()
