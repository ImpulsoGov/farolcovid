import sys
import os
from pathlib import Path 
current_path = Path().resolve()
abs_path = str(current_path.parent)
sys.path.append(abs_path)
sys.path.insert(0, '../')
sys.path.insert(0, '../src')


RAW_PATH = current_path / 'data' / 'raw'
TREAT_PATH = current_path / 'data' / 'treated'
OUTPUT_PATH = current_path / 'data' / 'output'
FIGURES_PATH = current_path / 'data' / 'figures'
THEMES_PATH = current_path / 'themes'