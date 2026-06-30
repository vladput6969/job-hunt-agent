"""
Smoke test for GoogleSource via python-jobspy.

Usage:
    python scripts/smoke_google.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.loader import load_config
from sources.google import GoogleSource
from store.search_criteria import SearchCriteria

CRITERIA = SearchCriteria(
    titles=["Software Engineer", "Backend Engineer"],
    locations=["Bangalore", "India"],
    remote=False,
)


def main() -> None:
    config = load_config()
    source = GoogleSource(config)

    print(f"Querying Google Jobs via jobspy (max {config.sources.google.max_results} results)...\n")

    results = source.fetch(CRITERIA)

    print(f"Total: {len(results)} opportunities\n")
    for opp in results[:10]:
        print(f"  [{opp.company or '?'}] {opp.role_title}")
        print(f"    {opp.location}")
        print(f"    {opp.source_url}")
        print()


if __name__ == "__main__":
    main()
