from __future__ import annotations

import uuid
from datetime import datetime, timezone

from config.app_config import AppConfig
from orchestrator.state import CycleState
from store.profile_doc import ProfileDoc
from store.search_criteria import SearchCriteria


class ProfileAgent:
    # TODO Phase 1 T11: replace with real PDF parsing + LLM extraction
    def run(self, state: CycleState, config: AppConfig) -> dict[str, object]:
        criteria = SearchCriteria(
            titles=["Software Engineer", "Backend Engineer"],
            locations=["Bangalore", "Remote"],
            remote=True,
            comp_min_lpa=20,
        )
        profile = ProfileDoc(
            profile_id=str(uuid.uuid4()),
            version=1,
            created_at=datetime.now(timezone.utc),
            is_active=True,
            personal={"name": "Stub User", "email": "stub@example.com"},
            skills=["Python", "Java", "MongoDB"],
            experience_years=5.0,
            seniority="mid",
            experience=[],
            preferences=criteria,
            source_files=[],
        )
        return {
            "profile_doc": profile,
            "profile": profile.model_dump(),
            "search_criteria": criteria.model_dump(),
        }
