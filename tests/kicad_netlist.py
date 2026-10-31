"""Read the nodes of a KiCad s-expression netlist using the standard library."""
import json
from pathlib import Path
import re


def children(tree, tag):
    return [item for item in tree if isinstance(item, list) and item[0] == tag]


def field(tree, tag):
    return children(tree, tag)[0][1]


def read_nets(path):
    tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^()\s]+', Path(path).read_text()))

    def parse():
        result = []
        for token in tokens:
            if token == ")":
                return result
            result.append(parse() if token == "(" else
                            json.loads(token) if token.startswith('"') else token)
        return result

    root = parse()[0]
    return {field(net, "name"): frozenset((field(node, "ref"), field(node, "pin"))
            for node in children(net, "node"))
            for net in children(children(root, "nets")[0], "net")}
