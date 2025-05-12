"""
Mesa Agent-Based Modeling Framework

Core Objects: Model, and Agent.
"""

import datetime

import my_mesa.space as space
import my_mesa.time as time
from my_mesa.agent import Agent
from my_mesa.batchrunner import batch_run
from my_mesa.datacollection import DataCollector
from my_mesa.model import Model

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
