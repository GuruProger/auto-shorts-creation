from pathlib import Path

# Get the path to the file
core_dir = Path(__file__).resolve().parent.parent  # Main directory
tmp_dir = core_dir / 'data/temp'
font_path = core_dir / 'fonts/bold_font.ttf'


# Check if the directory exists, and create it if not.
if not tmp_dir.exists():
    tmp_dir.mkdir(parents=True, exist_ok=True)