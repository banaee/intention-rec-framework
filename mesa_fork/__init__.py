"""
Mesa Agent-Based Modeling Framework

Core Objects: Model, and Agent.
"""

import datetime

import mesa_fork.space as space
import mesa_fork.time as time
from mesa_fork.agent import Agent
from mesa_fork.batchrunner import batch_run
from mesa_fork.datacollection import DataCollector
from mesa_fork.model import Model

__all__ = [
    "Model",
    "Agent",
    "time",
    "space",
    "DataCollector",
    "batch_run",
    "experimental",
]

__title__ = "mesa"
__version__ = "3.0.0a1"
__license__ = "Apache 2.0"
_this_year = datetime.datetime.now(tz=datetime.timezone.utc).date().year
__copyright__ = f"Copyright {_this_year} Project Mesa Team"
