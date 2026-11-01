"""Verify actual KiCad pin connections of the standalone inhibition study."""
import sys
from kicad_netlist import read_nets


nets = read_nets(sys.argv[1])
caps = ["C30", "C31", "C32", "C33"]
expected = [
    {("JINH1", "1"), ("U3", "14"), ("U4", "14"), ("U5", "14"), ("U6", "5"),
        ("U3", "2"), ("U3", "4"), ("U3", "10"), ("R30", "1"), ("R31", "1"), ("R34", "1")}
    | {(c, "1") for c in caps},
    {("JINH1", "2"), ("U3", "7"), ("U4", "7"), ("U5", "7"), ("U6", "2"),
        ("U3", "11"), ("U3", "12"), ("U3", "13"),
        ("U4", "3"), ("U4", "4"), ("U4", "5"), ("U4", "9"), ("U4", "10"), ("U4", "11"),
        ("U5", "5"), ("U5", "9"), ("U5", "11"), ("U5", "13"),
        ("R32", "2"), ("R33", "2"), ("SF1", "2")}
    | {(c, "2") for c in caps},
    {("U6", "1"), ("U5", "1"), ("R30", "2")},
    {("U5", "2"), ("U5", "3")},
    {("U5", "4"), ("U3", "1"), ("U4", "13"), ("JINH1", "6")},
    {("U6", "3"), ("R31", "2"), ("SF1", "1")},
    {("JINH1", "4"), ("U6", "4"), ("R32", "1")},
    {("JINH1", "3"), ("U3", "3"), ("U4", "2"), ("R33", "1")},
    {("U3", "5"), ("U4", "1"), ("JINH1", "5")},
    {("U4", "12"), ("R34", "2"), ("JINH1", "7")},
]
unused = {("U3", "6"), ("U3", "8"), ("U3", "9"),
    ("U4", "6"), ("U4", "8"), ("U5", "6"), ("U5", "8"), ("U5", "10"), ("U5", "12")}
connected = {nodes for nodes in nets.values() if not (len(nodes) == 1 and next(iter(nodes)) in unused)}
assert connected == {frozenset(nodes) for nodes in expected}, "Unexpected inhibition connections"
assert len(connected) == 10
print("10 inhibition nets verified: latch, NAND, Schmitt chain, watchdog, fault and unused inputs")
