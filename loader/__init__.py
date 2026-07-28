# __init__.py
from .text_loader import load_text_files
from .csv_loader import load_csv
from .file_reader import read_file

__all__ = ["load_text_files", "load_csv", "read_file"]
