from __future__ import annotations

from functools import partial

from typing import Any

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.mongodb import MongoDBSaver

from orchestrator.deps import Deps
from orchestrator.nodes import (
    load_profile_node,
    run_discovery_match_node,
    run_profile_agent_node,
    run_reporter_node,
    store_results_node,
)
from orchestrator.router import route_after_profile
from orchestrator.state import CycleState


def build_graph(deps: Deps) -> CompiledStateGraph[Any, Any, Any, Any]:
    builder: StateGraph[CycleState, CycleState, CycleState] = StateGraph(CycleState)

    builder.add_node("load_profile", partial(load_profile_node, deps=deps))
    builder.add_node("run_profile_agent", partial(run_profile_agent_node, deps=deps))
    builder.add_node("run_discovery_match", partial(run_discovery_match_node, deps=deps))
    builder.add_node("store_results", partial(store_results_node, deps=deps))
    builder.add_node("run_reporter", partial(run_reporter_node, deps=deps))

    builder.set_entry_point("load_profile")

    builder.add_conditional_edges(
        "load_profile",
        route_after_profile,
        {
            "profile_exists": "run_discovery_match",
            "no_profile": "run_profile_agent",
        },
    )
    builder.add_edge("run_profile_agent", "run_discovery_match")
    builder.add_edge("run_discovery_match", "store_results")
    builder.add_edge("store_results", "run_reporter")
    builder.add_edge("run_reporter", END)

    checkpointer = MongoDBSaver(deps.mongo_client)
    return builder.compile(checkpointer=checkpointer)


def make_initial_state(cycle_id: str) -> CycleState:
    return CycleState(
        cycle_id=cycle_id,
        profile=None,
        search_criteria=None,
        raw_opportunities=[],
        scored_opportunities=[],
        shortlisted=[],
        rejected=[],
        report_path=None,
        errors=[],
        token_spend=0.0,
        sources_queried=[],
    )
