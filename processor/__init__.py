# __init__.py
from .processor import process_text
from .parallel import run_parallel
from .sequential import run_sequential

__all__ = ["process_text", "run_parallel", "run_sequential"]
