"""Check the movable eight-LED bank, isolated output groups and inhibition."""
import sys
from kicad_netlist import read_nets

nets = read_nets(sys.argv[1])
expected = [
    {("U1", "9"), ("U2", "14")},
    {("JH1", "3"), ("U1", "14"), ("R19", "1")},
    {("JH1", "4"), ("U1", "11"), ("U2", "11"), ("R20", "1")},
    {("JH1", "5"), ("U1", "12"), ("U2", "12"), ("R21", "1")},
    {("JH1", "6"), ("R17", "1")},
    {("U1", "13"), ("U2", "13"), ("R17", "2"), ("R18", "2"), ("S1", "2")},
    {("JH1", "1"), ("U1", "16"), ("U2", "16"), ("U1", "10"), ("U2", "10"),
        ("C1", "1"), ("C2", "1"), ("C3", "1"), ("R18", "1"), ("S1", "1")},
    {("JH1", "2"), ("U1", "8"), ("U2", "8"), ("C1", "2"), ("C2", "2"),
        ("C3", "2"), ("R19", "2"), ("R20", "2"), ("R21", "2")}
    | {(f"D{i}", "1") for i in range(1, 9)},
]
pins = (15, 1, 2, 3, 4, 5, 6, 7)
for i in range(16):
    expected.append({(f"U{i//8+1}", str(pins[i%8])), (f"JOUT{i//8+1}", str(i%8+1))})
for i in range(8):
    expected.append({("JLED1", str(i+1)), (f"R{i+1}", "1")})
    expected.append({(f"R{i+1}", "2"), (f"D{i+1}", "2")})
# The final cascade output is deliberately unconnected and marked as such.
nonempty = {nodes for nodes in nets.values() if nodes != frozenset({("U2", "9")})}
assert nonempty == {frozenset(nodes) for nodes in expected}, "Unexpected bench connections"
assert len(nonempty) == 40
print("40 bench nets verified: 8 LED resistors/polarities, 2 separate output groups, cascade and inhibition")
