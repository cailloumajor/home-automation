"""Small deterministic KiCad drawing helper for the low-voltage bench."""
import json
from pathlib import Path
import re
import uuid


def quote(value):
    return json.dumps(value, ensure_ascii=False)


def effects(size=1.27):
    return f"(effects (font (size {size} {size})))"


def line(x1, y1, x2, y2):
    return f"(polyline (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (fill (type none)))"


def rectangle(x1, y1, x2, y2):
    return f"(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0) (type default)) (fill (type none)))"


class Drawing:
    def __init__(self, stem, library):
        self.stem, self.library = stem, library
        self.root = str(uuid.uuid5(uuid.NAMESPACE_URL, stem))
        self.counter = 0
        self.symbols, self.parts = {}, []

    def uid(self):
        self.counter += 1
        return str(uuid.uuid5(uuid.UUID(self.root), str(self.counter)))

    def define(self, name, ref, pins, graphics):
        pp = "".join(f'(pin passive line (at {x} {y} {angle}) (length 2.54) '
                        f'(name {quote(label)} {effects(1)}) (number "{num}" {effects(1)}))'
                        for num, label, x, y, angle in pins)
        self.symbols[name] = (f'(symbol "{self.library}:{name}" (pin_names (offset 0.5)) '
            '(exclude_from_sim no) (in_bom yes) (on_board yes) '
            f'(property "Reference" "{ref}" (at 0 6 0) {effects()}) '
            f'(property "Value" "{name}" (at 0 8 0) {effects()}) '
            f'(symbol "{name}_0_1" {graphics}) (symbol "{name}_1_1" {pp}))')

    def symbol(self, name, ref, value, x, y, angle=0, title_offset=7.62):
        self.parts.append(f'''(symbol (lib_id "{self.library}:{name}") (at {x} {y} {angle}) (unit 1)
            (in_bom yes) (on_board yes) (dnp no) (uuid "{self.uid()}")
            (property "Reference" "{ref}" (at {x} {y-title_offset} 0) {effects(1.1)})
            (property "Value" {quote(value)} (at {x} {y-title_offset+2.54} 0) {effects(1.1)})
            (property "Footprint" "" (at {x} {y} 0) (effects (font (size 1 1)) hide))
            (instances (project "{self.stem}" (path "/{self.root}" (reference "{ref}") (unit 1)))))''')

    def wire(self, x1, y1, x2, y2):
        self.parts.append(f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) '
                            f'(stroke (width 0) (type default)) (uuid "{self.uid()}"))')

    def label(self, name, x, y):
        self.parts.append(f'(label {quote(name)} (at {x} {y} 0) '
            f'(effects (font (size 1.1 1.1)) (justify left bottom)) (uuid "{self.uid()}"))')

    def no_connect(self, x, y):
        self.parts.append(f'(no_connect (at {x} {y}) (uuid "{self.uid()}"))')

    def text(self, value, x, y, size=1.5):
        self.parts.append(f'(text {quote(value)} (at {x} {y} 0) '
            f'(effects (font (size {size} {size})) (justify left)) (uuid "{self.uid()}"))')

    def save(self, directory, title, date="2026-10-31", revision="D-banc-TBT"):
        directory = Path(directory)
        def snap(match):
            tag, x, y = match.groups()
            return f'({tag} {round(round(float(x)/1.27)*1.27,4)} {round(round(float(y)/1.27)*1.27,4)}'
        placed = re.sub(r'\((at|xy) (-?[\d.]+) (-?[\d.]+)', snap, "\n".join(self.parts))
        libs = "\n".join(self.symbols.values())
        (directory / f"{self.stem}.kicad_sch").write_text(
            f'(kicad_sch (version 20250114) (generator "eeschema") '
            f'(uuid "{self.root}") (paper "A3") '
            f'(title_block (title {quote(title)}) (date {quote(date)}) (rev {quote(revision)})) '
            f'(lib_symbols {libs})\n{placed})\n')
        (directory / f"{self.stem}.kicad_pro").write_text('{}\n')
        local = libs.replace(f'(symbol "{self.library}:', '(symbol "')
        (directory / f"{self.library}.kicad_sym").write_text(
            f'(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") {local})\n')
