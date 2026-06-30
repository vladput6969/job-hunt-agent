from unittest.mock import patch

import pandas as pd

from config.app_config import AppConfig
from sources.google import GoogleSource
from store.search_criteria import SearchCriteria

_CRITERIA = SearchCriteria(
    titles=["Backend Engineer"],
    locations=["Bangalore"],
    remote=False,
)

_MOCK_DF = pd.DataFrame([
    {
        "id": "ggl_789",
        "title": "Backend Engineer",
        "company": "StartupXYZ",
        "location": "Bengaluru, Karnataka, India",
        "job_url": "https://jobs.google.com/view/ggl_789",
        "description": "Backend engineer role.",
    }
])

_EMPTY_DF = pd.DataFrame(
    columns=["id", "title", "company", "location", "job_url", "description"]
)


def test_fetch_returns_raw_opportunities(app_config: AppConfig) -> None:
    source = GoogleSource(app_config)

    with patch("sources.jobspy_base.scrape_jobs", return_value=_MOCK_DF):
        results = source.fetch(_CRITERIA)

    assert len(results) == 1
    opp = results[0]
    assert opp.source == "google"
    assert opp.role_title == "Backend Engineer"
    assert opp.external_id == "google:ggl_789"


def test_fetch_returns_empty_on_exception(app_config: AppConfig) -> None:
    source = GoogleSource(app_config)

    with patch("sources.jobspy_base.scrape_jobs", side_effect=Exception("blocked")):
        results = source.fetch(_CRITERIA)

    assert results == []


def test_fetch_respects_max_results(app_config: AppConfig) -> None:
    app_config.sources.google.max_results = 1
    source = GoogleSource(app_config)

    big_df = pd.concat([_MOCK_DF] * 5, ignore_index=True)
    with patch("sources.jobspy_base.scrape_jobs", return_value=big_df):
        results = source.fetch(_CRITERIA)

    assert len(results) <= 1


def test_is_enabled_false_when_disabled(app_config: AppConfig) -> None:
    source = GoogleSource(app_config)
    assert source.is_enabled(app_config) is False
