
from pathlib import Path
from datetime import datetime
import py_compile
import shutil

target = Path("views/dashboard.py")

if not target.exists():
    raise SystemExit("ERROR: views/dashboard.py was not found.")

source = target.read_text(encoding="utf-8")

marker = "# BRICK_8_EMOTION_SUMMARY"

if marker in source:
    raise SystemExit("Brick 8 is already present. No changes made.")

# Find the existing emotion chart section.
search_text = 'st.subheader("Emotion Distribution")'

if search_text not in source:
    search_text = 'st.subheader("Emotion Analysis")'

if search_text not in source:
    raise SystemExit(
        "Could not find the emotion chart heading. "
        "No changes made. Send me the emotion chart section."
    )

backup = target.with_name(
    f"dashboard.py.brick8-backup-{datetime.now():%Y%m%d-%H%M%S}"
)
shutil.copy2(target, backup)

# Insert a marker only; the actual KPI placement needs
# to match your existing emotion chart implementation.
source = source.replace(
    search_text,
    f"{marker}\n{search_text}",
    1,
)

temporary = target.with_suffix(".py.brick8-tmp")
temporary.write_text(source, encoding="utf-8")

try:
    py_compile.compile(str(temporary), doraise=True)
    temporary.replace(target)
    print("Brick 8 marker added successfully.")
    print(f"Backup saved at: {backup}")
    print("Next, we will add the KPI in the correct location.")
except Exception:
    temporary.unlink(missing_ok=True)
    raise
