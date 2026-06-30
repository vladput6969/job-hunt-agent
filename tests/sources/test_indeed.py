from unittest.mock import patch

import pandas as pd

from config.app_config import AppConfig
from sources.indeed import IndeedSource
from store.search_criteria import SearchCriteria

_CRITERIA = SearchCriteria(
    titles=["Backend Engineer"],
    locations=["Bangalore"],
    remote=False,
)

_MOCK_DF = pd.DataFrame([
    {
        "id": "ind_456",
        "title": "Senior Backend Engineer",
        "company": "TechCorp",
        "location": "Bengaluru, Karnataka, India",
        "job_url": "https://in.indeed.com/jobs/view/ind_456",
        "description": "Looking for a backend engineer.",
    }
])

_EMPTY_DF = pd.DataFrame(
    columns=["id", "title", "company", "location", "job_url", "description"]
)


def test_fetch_returns_raw_opportunities(app_config: AppConfig) -> None:
    source = IndeedSource(app_config)

    with patch("sources.jobspy_base.scrape_jobs", return_value=_MOCK_DF):
        results = source.fetch(_CRITERIA)

    assert len(results) == 1
    opp = results[0]
    assert opp.source == "indeed"
    assert opp.role_title == "Senior Backend Engineer"
    assert opp.external_id == "indeed:ind_456"


def test_fetch_returns_empty_on_exception(app_config: AppConfig) -> None:
    source = IndeedSource(app_config)

    with patch("sources.jobspy_base.scrape_jobs", side_effect=Exception("blocked")):
        results = source.fetch(_CRITERIA)

    assert results == []


def test_fetch_respects_max_results(app_config: AppConfig) -> None:
    app_config.sources.indeed.max_results = 1
    source = IndeedSource(app_config)

    big_df = pd.concat([_MOCK_DF] * 5, ignore_index=True)
    with patch("sources.jobspy_base.scrape_jobs", return_value=big_df):
        results = source.fetch(_CRITERIA)

    assert len(results) <= 1


def test_is_enabled_reads_config(app_config: AppConfig) -> None:
    source = IndeedSource(app_config)
    assert source.is_enabled(app_config) is True
