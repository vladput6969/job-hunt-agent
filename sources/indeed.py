from config.sources.indeed_config import IndeedConfig
from sources.jobspy_base import JobSpyBase


class IndeedSource(JobSpyBase):
    name: str = "indeed"
    site_name: str = "indeed"

    def _extra_kwargs(self) -> dict[str, object]:
        cfg: IndeedConfig = self._config.sources.indeed
        return {"country_indeed": cfg.country}
