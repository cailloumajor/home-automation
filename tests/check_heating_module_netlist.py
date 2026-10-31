"""Check the exported KiCad netlist topology, including polarity and isolation.

Usage: python tests/check_heating_module_netlist.py /tmp/heating-v03-module.net
This checks connections only, not electrical suitability or PCB isolation.
"""
import json
from pathlib import Path
import re
import sys


tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^()\s]+',
                            Path(sys.argv[1]).read_text()))


def parse():
    result = []
    for token in tokens:
        if token == ")":
            return result
        result.append(parse() if token == "(" else
                        json.loads(token) if token.startswith('"') else token)
    return result


def children(tree, tag):
    return [item for item in tree if isinstance(item, list) and item[0] == tag]


def field(tree, tag):
    return children(tree, tag)[0][1]


root = parse()[0]
nets = {}
for net in children(children(root, "nets")[0], "net"):
    nodes = frozenset((field(node, "ref"), field(node, "pin"))
                        for node in children(net, "node"))
    assert len(nodes) >= 2, ("Dangling net", field(net, "name"))
    nets[field(net, "name")] = nodes

expected = []
expected.append({("J1", "1")} | {(f"R{i}1", "1") for i in range(1, 5)})
expected.append({("J1", "2")} | {(f"Q{i}", "2") for i in range(1, 5)}
                | {(f"R{i}3", "1") for i in range(1, 5)})
expected.append({("J2", "1")} | {(f"U{i}", "4") for i in range(1, 5)})
for i in range(1, 5):
    expected.extend([
        {("J1", str(i+2)), (f"R{i}2", "1")},
        {(f"R{i}2", "2"), (f"R{i}3", "2"), (f"Q{i}", "1")},
        {(f"Q{i}", "3"), (f"U{i}", "2")},
        {(f"R{i}1", "2"), (f"U{i}", "1")},
        {(f"U{i}", "3"), (f"D{i}", "2" if i % 2 else "1")},
    ])
for channel in (1, 2):
    expected.append({("J2", str(channel+1)), (f"D{channel*2-1}", "1"),
                        (f"D{channel*2}", "2")})

assert set(nets.values()) == {frozenset(n) for n in expected}, "Unexpected topology"
assert len(nets) == 25

# No conductive path crosses the optical barrier in this netlist.
def is_hv(ref, pin):
    return ref.startswith("D") or ref == "J2" or (ref.startswith("U") and pin in ("3", "4"))


assert all(len({is_hv(*node) for node in nodes}) == 1 for nodes in nets.values())
print("25 nets verified: four branches, diode polarities, two outputs and TBT/sector separation")
