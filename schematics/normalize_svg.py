"""Normalize trailing whitespace in KiCad SVG exports before committing."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


for name in sys.argv[1:]:
    path = Path(name)
    ET.parse(path)
    content = "\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n"
    ET.fromstring(content)
    path.write_text(content)
