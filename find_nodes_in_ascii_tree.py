"""
Find which of the requested nodes (witnesses) exist in the given ascii tree file.

(ASCII trees can be created with my nexus_tree_to_ascii.py script)
"""


# Chars used for the tree
TREE_ART = ('|', '_', ',')


def find(in_f, nodes):
    found_nodes = set()
    with open(in_f) as f:
        for line in f:
            if not line.strip():
                continue
            line_node = line.split()[-1]
            if line_node not in TREE_ART:
                if line_node in nodes:
                    found_nodes.add(line_node)

    print("Found: {}".format(' '.join(sorted(found_nodes))))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find nodes in an ASCII tree")
    parser.add_argument('inputfile', help='.con.tre NEXUS file')
    parser.add_argument('node', help='a node (can be specified multiple times)', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    find(args.inputfile, set(args.node))
