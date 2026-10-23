from pathlib import Path
from datetime import datetime
import py_compile
import sys

target = Path("views/dashboard.py")

if not target.exists():
    sys.exit("STOP: Dashboard file not found. No changes made.")

source = target.read_text()
marker = "# BRICK_5_PREMIUM_LIGHT_STYLE"
call = "    apply_dashboard_styles()\n"

if marker in source:
    sys.exit("Brick 5 already exists. No changes made.")

if source.count(call) != 1 or "def show():" not in source:
    sys.exit("STOP: Dashboard structure differs. No changes made.")

helper = '''
# BRICK_5_PREMIUM_LIGHT_STYLE
def apply_premium_light_style():
    """Apply premium light styling without changing analytics."""
    st.markdown("""
    <style>
    .stApp {
        background: #f6f8fc;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #f8faff);
        border: 1px solid #e3e9f4;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 4px 16px rgba(28, 48, 86, 0.045);
    }

    [data-testid="stMetricLabel"] {
        color: #66748b;
        font-size: 0.88rem;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #172b4d;
        font-weight: 750;
        letter-spacing: -0.035em;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #e3e9f4;
        border-radius: 16px;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3 {
        color: #172b4d;
        letter-spacing: -0.025em;
    }

    .stMarkdown h2 {
        margin-top: 1.25rem;
        margin-bottom: 0.65rem;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    .stButton > button:hover {
        border-color: #7796d8;
        box-shadow: 0 3px 12px rgba(55, 94, 170, 0.10);
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid #e3e9f4;
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)
'''

updated = source.replace("def show():", helper + "\ndef show():", 1)
updated = updated.replace(
    call, call + "    apply_premium_light_style()\n", 1
)

if updated == source:
    sys.exit("STOP: Could not prepare the change. No changes made.")

backup = target.with_name(
    f"dashboard.py.brick5-backup-{datetime.now():%Y%m%d-%H%M%S}"
)
temporary = target.with_name("dashboard.py.brick5-tmp")

try:
    backup.write_text(source)
    temporary.write_text(updated)
    py_compile.compile(str(temporary), doraise=True)
    target.write_text(updated)
    print("SUCCESS: Premium light styling applied.")
    print("Python syntax test: PASSED")
    print(f"Backup: {backup}")
except Exception as exc:
    print(f"FAILED: {exc}")
    print("Stop and send me this error.")
    sys.exit(1)
finally:
    if temporary.exists():
        temporary.unlink()
