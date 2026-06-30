"""
Smoke test: runs the full LangGraph pipeline against a live local MongoDB.
Uses stub agents — no LLM calls, no source fetches.
Verifies that all nodes execute, state propagates, and MongoDB is updated.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pymongo import MongoClient

from agents.discovery_match_agent import DiscoveryMatchAgent
from agents.profile_agent import ProfileAgent
from agents.reporter_agent import ReporterAgent
from config.loader import load_config, reset_config_cache
from orchestrator.deps import Deps
from orchestrator.graph import build_graph, make_initial_state
from store.cycle_record import CycleRecord
from store.db import get_client
from store.repositories.cycle_repo import CycleRepository
from store.repositories.opportunity_repo import OpportunityRepository
from store.repositories.profile_repo import ProfileRepository


TEST_DB = "test_job_hunt"


@pytest.fixture(autouse=True)
def reset_config() -> None:
    reset_config_cache()


@pytest.fixture
def mongo_client() -> MongoClient:  # type: ignore[type-arg]
    reset_config_cache()
    config = load_config()
    return get_client(config.mongodb)


@pytest.fixture
def deps(mongo_client: MongoClient) -> Deps:  # type: ignore[type-arg]
    reset_config_cache()
    config = load_config()
    db = mongo_client[TEST_DB]
    return Deps(
        config=config,
        mongo_client=mongo_client,
        db=db,
        profile_repo=ProfileRepository(db),
        opportunity_repo=OpportunityRepository(db),
        cycle_repo=CycleRepository(db),
        source_registry=[],
        profile_agent=ProfileAgent(),
        discovery_match_agent=DiscoveryMatchAgent(),
        reporter_agent=ReporterAgent(),
    )


def test_graph_runs_full_cycle_no_profile(deps: Deps, mongo_client: MongoClient) -> None:  # type: ignore[type-arg]
    """Graph creates a profile when none exists, then runs discovery → store → report."""
    db = mongo_client[TEST_DB]
    db["profiles"].delete_many({})
    db["cycles"].delete_many({})
    db["opportunities"].delete_many({})

    cycle_id = str(uuid.uuid4())
    deps.cycle_repo.create(
        CycleRecord(cycle_id=cycle_id, started_at=datetime.now(timezone.utc))
    )

    graph = build_graph(deps)
    final_state = graph.invoke(
        make_initial_state(cycle_id),
        config={"configurable": {"thread_id": cycle_id}},
    )

    assert final_state["profile"] is not None
    assert final_state["search_criteria"] is not None
    assert final_state["report_path"] is not None

    cycle = deps.cycle_repo.get_latest()
    assert cycle is not None
    assert cycle.cycle_id == cycle_id
    assert cycle.completed_at is not None
    assert cycle.report_path == final_state["report_path"]


def test_graph_skips_profile_agent_when_profile_exists(deps: Deps, mongo_client: MongoClient) -> None:  # type: ignore[type-arg]
    """Graph skips run_profile_agent when an active profile already exists."""
    db = mongo_client[TEST_DB]
    db["profiles"].delete_many({})
    db["cycles"].delete_many({})

    # Pre-seed a profile so load_profile_node finds it
    seed_result = deps.profile_agent.run({}, deps.config)  # type: ignore[arg-type]
    deps.profile_repo.save(seed_result["profile_doc"])  # type: ignore[arg-type]

    cycle_id = str(uuid.uuid4())
    deps.cycle_repo.create(
        CycleRecord(cycle_id=cycle_id, started_at=datetime.now(timezone.utc))
    )

    graph = build_graph(deps)
    final_state = graph.invoke(
        make_initial_state(cycle_id),
        config={"configurable": {"thread_id": cycle_id}},
    )

    assert final_state["profile"] is not None
    assert final_state["report_path"] is not None
