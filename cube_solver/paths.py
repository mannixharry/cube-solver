'''Filesystem paths for resources and generated lookup tables.

Paths are resolved relative to this package's location (not the current
working directory), so the program behaves the same whether launched via
`python run.py`, from a different directory, or bundled by PyInstaller.
'''
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    PROJECT_ROOT = Path(sys._MEIPASS)  # PyInstaller bundle
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESOURCES_DIR = PROJECT_ROOT / 'resources'
MOVE_TABLES_DIR = PROJECT_ROOT / 'tables' / 'move_tables'
PRUNING_TABLES_DIR = PROJECT_ROOT / 'tables' / 'pruning_tables'
