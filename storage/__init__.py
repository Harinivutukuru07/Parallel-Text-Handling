# __init__.py
from .database import setup_database, apply_indexes
from .queries import insert_results, get_sample_results
from .benchmark import benchmark_queries

__all__ = ["setup_database", "apply_indexes", "insert_results", "get_sample_results", "benchmark_queries"]
