from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pymongo import MongoClient
from pymongo.database import Database

from config.app_config import AppConfig
from sources.interfaces import IJobSource
from store.repositories.cycle_repo import CycleRepository
from store.repositories.opportunity_repo import OpportunityRepository
from store.repositories.profile_repo import ProfileRepository


@dataclass
class Deps:
    config: AppConfig
    mongo_client: MongoClient[dict[str, Any]]
    db: Database[dict[str, Any]]
    profile_repo: ProfileRepository
    opportunity_repo: OpportunityRepository
    cycle_repo: CycleRepository
    source_registry: list[IJobSource]
    profile_agent: Any  # typed in T11
    discovery_match_agent: Any  # typed in T12
    reporter_agent: Any  # typed in T13
