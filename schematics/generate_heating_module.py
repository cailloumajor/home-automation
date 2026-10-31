"""Generate the editable, provisional two-channel schematic (no PCB).

All symbols are embedded. Pin numbering follows TLP240JF and BC847.
Run from any directory; generated files are adjacent to this script.
"""
from pathlib import Path
import json
import re
import uuid

HERE = Path(__file__).resolve().parent
ROOT = str(uuid.uuid5(uuid.NAMESPACE_URL, "heating-controller-v03-module"))
parts = []
counter = 0


def uid():
    global counter
    counter += 1
    return str(uuid.uuid5(uuid.UUID(ROOT), str(counter)))


def q(value):
    return json.dumps(value, ensure_ascii=False)


def fx(size=1.27):
    return f"(effects (font (size {size} {size})))"


def line(x1, y1, x2, y2):
    return f"(polyline (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (fill (type none)))"


def library(name, ref, pins, graphics):
    pp = "".join(f'(pin passive line (at {x} {y} {a}) (length 2.54) '
                    f'(name {q(n)} {fx(0.9)}) (number "{p}" {fx(0.9)}))'
                    for p, n, x, y, a in pins)
    return (f'(symbol "Heating:{name}" (pin_names (offset 0.5)) '
            f'(exclude_from_sim no) (in_bom yes) (on_board yes) '
            f'(property "Reference" "{ref}" (at 0 6 0) {fx()}) '
            f'(property "Value" "{name}" (at 0 8 0) {fx()}) '
            f'(symbol "{name}_0_1" {graphics}) '
            f'(symbol "{name}_1_1" {pp}))')


box = '(rectangle (start -5.08 3.81) (end 5.08 -3.81) (stroke (width 0) (type default)) (fill (type none)))'
libs = [
    library("R", "R", [(1, "", -5.08, 0, 0), (2, "", 5.08, 0, 180)],
            '(rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0) (type default)) (fill (type none)))'),
    library("D", "D", [(1, "K", -5.08, 0, 0), (2, "A", 5.08, 0, 180)],
            line(-1.27, -1.27, -1.27, 1.27) +
            '(polyline (pts (xy -1.27 0) (xy 1.27 1.27) (xy 1.27 -1.27) (xy -1.27 0)) (stroke (width 0) (type default)) (fill (type none)))'),
    library("NPN", "Q", [(1, "B", -7.62, 0, 0), (2, "E", 2.54, -6.35, 90), (3, "C", 2.54, 6.35, 270)], box),
    library("TLP240JF", "U", [(1, "A", -7.62, 2.54, 0), (2, "K", -7.62, -2.54, 0),
                                (3, "S", 7.62, -2.54, 180), (4, "S", 7.62, 2.54, 180)],
            box + line(0, -3.81, 0, 3.81)),
]
for count in (3, 6):
    libs.append(library(f"Conn{count}", "J",
                        [(i+1, "", 7.62, -i*2.54, 180) for i in range(count)],
                        f'(rectangle (start -2.54 2.54) (end 5.08 {-count*2.54}) '
                        '(stroke (width 0) (type default)) (fill (type none)))'))


def symbol(name, ref, value, x, y, angle=0):
    rx, ry, vx, vy, pa = x, y-6, x, y-3.8, 0
    if name == "TLP240JF":
        ry, vy = y-9, y-6.5
    elif name == "NPN":
        rx, ry, vx, vy = x+17, y-1.27, x+17, y+1.27
    elif name == "R" and angle == 90:
        rx, ry, vx, vy, pa = x-9, y-1.27, x-9, y+1.27, 90
    parts.append(f'''(symbol (lib_id "Heating:{name}") (at {x} {y} {angle}) (unit 1)
        (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")
        (property "Reference" "{ref}" (at {rx} {ry} {pa}) {fx()})
        (property "Value" {q(value)} (at {vx} {vy} {pa}) {fx(1.05)})
        (property "Footprint" "" (at {x} {y} 0) (effects (font (size 1 1)) hide))
        (instances (project "heating_controller_v03_module"
        (path "/{ROOT}" (reference "{ref}") (unit 1)))))''')


def wire(x1, y1, x2, y2):
    if (x1, y1) != (x2, y2):
        parts.append(f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) '
                        f'(stroke (width 0) (type default)) (uuid "{uid()}"))')


def label(name, x, y):
    parts.append(f'(label {q(name)} (at {x} {y} 0) '
                    f'(effects (font (size 1.15 1.15)) (justify left bottom)) (uuid "{uid()}"))')


def text(value, x, y, size=1.5):
    parts.append(f'(text {q(value)} (at {x} {y} 0) '
                    f'(effects (font (size {size} {size})) (justify left)) (uuid "{uid()}"))')


text("V0.3 - MODULE 2 VOIES - ETUDE B / NON QUALIFIE POUR REALISATION SECTEUR", 25, 20, 2)
text("TBT a gauche / contacts secteur a droite. Protections et sectionnement externes NON DESSINES.", 25, 27)
text("Valeurs TBT provisoires. Empreintes, isolation PCB, surtensions et courts-circuits restent a dimensionner.", 25, 33)
text("Quatre commandes 3,3 V deja inhibees par OE + watchdog de la carte logique.", 25, 39)

for idx, (y, channel, polarity) in enumerate([(60, 1, "POS"), (110, 1, "NEG"),
                                            (170, 2, "POS"), (220, 2, "NEG")], 1):
    text(f"VOIE {channel} / {polarity}", 25, y-10, 1.7)
    symbol("R", f"R{idx}1", "560R 1% / 0,125W", 110, y-2.54)
    wire(95, y-2.54, 104.92, y-2.54)
    label("+5V_LED", 95, y-2.54)
    wire(115.08, y-2.54, 132.38, y-2.54)
    symbol("TLP240JF", f"U{idx}", "TLP240JF / candidat", 140, y)
    symbol("NPN", f"Q{idx}", "BC847B / candidat", 115, y+15.24)
    wire(132.38, y+2.54, 117.54, y+2.54)
    wire(117.54, y+2.54, 117.54, y+8.89)
    symbol("R", f"R{idx}2", "2k2 1%", 90, y+15.24)
    label(f"CH{channel}_{polarity}", 65, y+15.24)
    wire(65, y+15.24, 84.92, y+15.24)
    wire(95.08, y+15.24, 107.38, y+15.24)
    # Base-emitter pull-down, vertical resistor.
    symbol("R", f"R{idx}3", "47k 1%", 100, y+25.4, 90)
    wire(100, y+15.24, 100, y+20.32)
    parts.append(f'(junction (at 100 {y+15.24}) (diameter 0) (color 0 0 0 0) (uuid "{uid()}"))')
    wire(100, y+30.48, 100, y+33.02)
    wire(117.54, y+21.59, 117.54, y+33.02)
    wire(100, y+33.02, 117.54, y+33.02)
    label("GND_TBT", 100, y+33.02)
    label("L_CMD", 155, y-2.54)
    wire(147.62, y-2.54, 155, y-2.54)
    wire(147.62, y+2.54, 175, y+2.54)
    # D has K on left by default: rotate 180 degrees for positive path.
    symbol("D", f"D{idx}", "1N4007 / candidat", 180.08, y+2.54,
            180 if polarity == "POS" else 0)
    wire(185.16, y+2.54, 210, y+2.54)
    label(f"FP{channel}", 210, y+2.54)

symbol("Conn6", "J1", "Interface TBT / provisoire", 290, 75)
for i, net in enumerate(("+5V_LED", "GND_TBT", "CH1_POS", "CH1_NEG", "CH2_POS", "CH2_NEG")):
    wire(297.62, 75+i*2.54, 315, 75+i*2.54)
    label(net, 315, 75+i*2.54)
symbol("Conn3", "J2", "Interface secteur / provisoire", 290, 185)
for i, net in enumerate(("L_CMD", "FP1", "FP2")):
    wire(297.62, 185+i*2.54, 315, 185+i*2.54)
    label(net, 315, 185+i*2.54)
text("L_CMD : source du circuit associe", 265, 205, 1.15)
text("Neutre : reference externe des radiateurs", 265, 212, 1.15)
text("Aucun neutre sur ce module", 265, 219, 1.15)

text("Pas de liaison GND_TBT / neutre. Les noms identiques sont relies dans ce module uniquement.", 25, 266)
text("LED eteintes = contacts ouverts = absence de signal : CONFORT possible, pas ARRET garanti.", 25, 273)
text("Le schema de principe ne contient ni borniers definitifs, ni fusibles, ni parafoudres valides.", 25, 280)

def snap(match):
    tag, x, y = match.groups()
    return f'({tag} {round(round(float(x)/1.27)*1.27, 4)} {round(round(float(y)/1.27)*1.27, 4)}'


# Keep all placed pins, junctions and wire ends on KiCad's 50 mil grid.
placed = re.sub(r'\((at|xy) (-?[\d.]+) (-?[\d.]+)', snap, "\n".join(parts))
out = (f'(kicad_sch (version 20250114) (generator "eeschema") '
        f'(uuid "{ROOT}") (paper "A3") '
        '(title_block (title "Heating controller - module 2 voies - PROVISOIRE") '
        '(date "2026-10-31") (rev "B-etude") '
        '(comment 1 "NON QUALIFIE SECTEUR - VOIR NOTE DE DIMENSIONNEMENT")) '
        '(lib_symbols ' + "\n".join(libs) + ')\n' + placed + ')\n')
(HERE / "heating_controller_v03_module.kicad_sch").write_text(out)
(HERE / "Heating.kicad_sym").write_text(
    '(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'
    + "\n".join(s.replace('(symbol "Heating:', '(symbol "', 1) for s in libs) + ')\n')
(HERE / "sym-lib-table").write_text(
    '(sym_lib_table (version 7)\n'
    '  (lib (name "Heating") (type "KiCad") (uri "${KIPRJMOD}/Heating.kicad_sym") (options "") (descr "Provisional heating module symbols"))\n'
    '  (lib (name "HeatingBench") (type "KiCad") (uri "${KIPRJMOD}/HeatingBench.kicad_sym") (options "") (descr "USB LED bench symbols")))\n')
