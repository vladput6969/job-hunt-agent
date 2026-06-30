from config.sources.base import SourcePolicyBase


class JobSpyConfig(SourcePolicyBase):
    max_results: int = 50
    hours_old: int = 72
