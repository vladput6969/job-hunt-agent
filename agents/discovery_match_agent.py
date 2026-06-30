from __future__ import annotations

from config.app_config import AppConfig
from orchestrator.state import CycleState


class DiscoveryMatchAgent:
    # TODO Phase 1 T12: replace with real source fetching + LLM scoring
    def run(self, state: CycleState, config: AppConfig) -> dict[str, object]:
        return {
            "raw_opportunities": [],
            "scored_opportunities": [],
            "shortlisted": [],
            "rejected": [],
            "token_spend": 0.0,
            "sources_queried": [],
        }
