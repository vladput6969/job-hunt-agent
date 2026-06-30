from __future__ import annotations

from pathlib import Path

from config.app_config import AppConfig
from orchestrator.state import CycleState


class ReporterAgent:
    # TODO Phase 1 T13: replace with real Markdown report generation
    def run(self, state: CycleState, config: AppConfig) -> dict[str, object]:
        report_path = Path("output") / f"report_{state['cycle_id']}.md"
        report_path.write_text(
            f"# Job Hunt Report\n\n"
            f"**Cycle:** {state['cycle_id']}\n"
            f"**Shortlisted:** {len(state['shortlisted'])}\n"
            f"**Rejected:** {len(state['rejected'])}\n"
        )
        return {"report_path": str(report_path)}
