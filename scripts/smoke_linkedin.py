"""
Smoke test for LinkedInSource — real HTTP via python-jobspy, no credentials needed.

Usage:
    python scripts/smoke_linkedin.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.loader import load_config
from sources.linkedin import LinkedInSource
from store.search_criteria import SearchCriteria

CRITERIA = SearchCriteria(
    titles=["Software Engineer", "Backend Engineer"],
    locations=["Bangalore", "India"],
    remote=False,
)


def main() -> None:
    config = load_config()
    source = LinkedInSource(config)

    print(f"Querying LinkedIn via jobspy (max {config.sources.linkedin.max_results} results)...\n")

    results = source.fetch(CRITERIA)

    print(f"Total: {len(results)} opportunities\n")
    for opp in results[:10]:
        print(f"  [{opp.company or '?'}] {opp.role_title}")
        print(f"    {opp.location}")
        print(f"    {opp.source_url}")
        print()


if __name__ == "__main__":
    main()
