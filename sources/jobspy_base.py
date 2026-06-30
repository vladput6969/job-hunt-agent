from jobspy import scrape_jobs

from config.app_config import AppConfig
from config.sources.jobspy_config import JobSpyConfig
from store.raw_opportunity import RawOpportunity
from store.search_criteria import SearchCriteria
from store.source_policy import SourcePolicy


class JobSpyBase:
    """Base for all sources backed by python-jobspy (LinkedIn, Indeed, Google)."""

    name: str
    site_name: str
    policy: SourcePolicy = SourcePolicy.allowed

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def _extra_kwargs(self) -> dict[str, object]:
        return {}

    def _source_cfg(self) -> JobSpyConfig:
        cfg: JobSpyConfig = getattr(self._config.sources, self.name)
        return cfg

    def fetch(self, criteria: SearchCriteria) -> list[RawOpportunity]:
        cfg = self._source_cfg()
        max_results = cfg.max_results
        hours_old = cfg.hours_old
        results: list[RawOpportunity] = []

        for title in criteria.titles:
            for location in criteria.locations:
                if len(results) >= max_results:
                    return results
                try:
                    df = scrape_jobs(
                        site_name=[self.site_name],
                        search_term=title,
                        location=location,
                        results_wanted=min(10, max_results - len(results)),
                        hours_old=hours_old,
                        verbose=0,
                        **self._extra_kwargs(),
                    )
                except Exception:
                    continue

                for _, row in df.iterrows():
                    if len(results) >= max_results:
                        return results
                    results.append(
                        RawOpportunity(
                            source=self.name,
                            source_url=str(row.get("job_url", "")),
                            external_id=f"{self.name}:{row.get('id', '')}",
                            company=str(row.get("company", "") or ""),
                            role_title=str(row.get("title", "") or ""),
                            location=str(row.get("location", "") or ""),
                            description_raw=str(row.get("description", "") or ""),
                        )
                    )

        return results

    def is_enabled(self, config: AppConfig) -> bool:
        return self._source_cfg().enabled
