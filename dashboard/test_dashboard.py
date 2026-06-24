"""
test_dashboard.py
==================
Headless validation of every page in the Streamlit dashboard using
Streamlit's official AppTest framework (no browser needed). Run with:

    python dashboard/test_dashboard.py

This was used during development to catch runtime errors (bad column
names, etc.) on every one of the 11 pages before shipping.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent / "app.py")

PAGES = [
    "🏠 Executive Overview",
    "🌍 Global Content Map",
    "🎭 Genre Analysis",
    "🌐 Country Performance",
    "📈 Release Trend Dashboard",
    "⭐ Ratings Dashboard",
    "🎞️ Movie vs TV Dashboard",
    "🔍 Title Search & Detail",
    "🏆 Director & Actor Rankings",
    "📅 Netflix Expansion Timeline",
    "📌 Executive Summary & Recommendations",
]


def main():
    failures = []
    for page in PAGES:
        at = AppTest.from_file(APP_PATH, default_timeout=120)
        at.run()
        if at.exception:
            failures.append((page, "initial run", at.exception[0].value))
            continue
        # Select the page via the sidebar radio (first radio widget)
        at.sidebar.radio[0].set_value(page).run()
        if at.exception:
            failures.append((page, "after page select", at.exception[0].value))
        else:
            print(f"[PASS] {page}  ({len(at.main.children)} top-level elements rendered)")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} PAGE(S) FAILED:")
        for page, stage, err in failures:
            print(f"  ❌ {page} [{stage}]: {err}")
        sys.exit(1)
    else:
        print(f"ALL {len(PAGES)} PAGES PASSED ✅")


if __name__ == "__main__":
    main()
