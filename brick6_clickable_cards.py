from pathlib import Path
from datetime import datetime
import py_compile
import sys

target = Path("views/dashboard.py")

if not target.exists():
    sys.exit("STOP: views/dashboard.py not found.")

source = target.read_text()

start_marker = "# BRICK_1_UNIFIED_PLATFORM_OVERVIEW"
end_marker = "# BRICK_5_PREMIUM_LIGHT_STYLE"

if start_marker not in source or end_marker not in source:
    sys.exit("STOP: Expected dashboard section markers were not found.")

start = source.index(start_marker)
end = source.index(end_marker, start)

old_section = source[start:end]

if "BRICK_6_CLICKABLE_PLATFORM_CARDS" in old_section:
    sys.exit("Brick 6 already exists. No changes made.")

new_section = '''# BRICK_1_UNIFIED_PLATFORM_OVERVIEW
# BRICK_6_CLICKABLE_PLATFORM_CARDS
def render_platform_overview():
    """Show platform status and navigate to tools from available cards."""
    platforms = [
        ("YouTube", "Available", "Existing project integration",
         "📺 YouTube Analyzer"),
        ("Text Analysis", "Available", "Analyze text",
         "📝 Text Analyzer"),
        ("CSV Upload", "Available", "Analyze uploaded datasets",
         "📂 CSV Upload"),
        ("Instagram", "Planned", "Authorized API integration required", None),
        ("Facebook", "Planned", "Authorized API integration required", None),
        ("X", "Planned", "Authorized API integration required", None),
        ("Reddit", "Planned", "API integration required", None),
        ("LinkedIn", "Planned", "Authorized API integration required", None),
        ("TikTok", "Planned", "Authorized API integration required", None),
    ]

    st.markdown("---")
    st.markdown("# Social Media Command Center")
    st.caption(
        "A unified overview of current analysis tools and future integrations."
    )

    available = sum(status == "Available" for _, status, _, _ in platforms)
    metrics = st.columns(3)
    metrics[0].metric("Platforms listed", len(platforms))
    metrics[1].metric("Available tools", available)
    metrics[2].metric("Planned integrations", len(platforms) - available)

    st.markdown("## Explore platforms")

    for start in range(0, len(platforms), 3):
        columns = st.columns(3)
        for column, (name, status, description, destination) in zip(
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

                    if destination:
                        if st.button(
                            f"Open {name}",
                            key=f"platform_open_{name.lower().replace(' ', '_')}",
                            use_container_width=True,
                        ):
                            st.session_state["navigation_page"] = destination
                            st.rerun()
                    else:
                        st.button(
                            "Not connected",
                            key=f"platform_unavailable_{name.lower()}",
                            disabled=True,
                            use_container_width=True,
                        )

    st.markdown("---")


'''

updated = source[:start] + new_section + source[end:]

# Confirm we are changing only the platform overview section.
if updated == source:
    sys.exit("STOP: No changes prepared.")

backup = target.with_name(
    f"dashboard.py.brick6-backup-{datetime.now():%Y%m%d-%H%M%S}"
)
temporary = target.with_name("dashboard.py.brick6-tmp")

try:
    backup.write_text(source)
    temporary.write_text(updated)
    py_compile.compile(str(temporary), doraise=True)
    target.write_text(updated)
    print("SUCCESS: Clickable platform cards installed.")
    print("Python syntax test: PASSED")
    print(f"Backup saved at: {backup}")
except Exception as exc:
    print(f"FAILED: {exc}")
    print("Stop and send me the error.")
    sys.exit(1)
finally:
    if temporary.exists():
        temporary.unlink()
