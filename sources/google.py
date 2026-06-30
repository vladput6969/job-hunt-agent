from sources.jobspy_base import JobSpyBase

# TODO Phase 2+: consider adding GlassdoorSource(JobSpyBase) here —
# site_name="glassdoor" gives salary range data useful for scoring.


class GoogleSource(JobSpyBase):
    name: str = "google"
    site_name: str = "google"
