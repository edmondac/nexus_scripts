"""
Convert an DOT file to a Pajek NET file.

This is designed to work with my DOT files, and might not convert everything
in generic DOT files.
"""

import sys
import logging
import os
import pydot


logger = logging.getLogger(__name__)


def parse_dot(dot_f):
    """
    Parse a dot file
    """
    with open(dot_f) as f:
        text = f.read()

    # G = Source(text)
    G = pydot.graph_from_dot_data(text)
    assert len(G) == 1
    return G[0]


def convert(dot_f, net_f):
    """
    Convert a dot file into Pajek NET format
    """
    G = parse_dot(dot_f)

    # Nodes
    nodes = sorted(G.get_nodes(), key=lambda x: x.obj_dict['sequence'])
    node_map = {}
    output = ['*Vertices {}'.format(len(nodes))]
    for node in nodes:  # already sorted by 'sequence'
        attr = node.obj_dict.get('attributes')
        if attr:
            logger.warning("Node has attributes - don't know what to do: %s", node.obj_dict)

        # Add the raw name to the node map
        node_map[node.obj_dict['name']] = node.obj_dict['sequence']

        # Sometimes the name is quoted
        name = node.obj_dict['name'].replace('"', '')

        output.append('{} "{}"'.format(node.obj_dict['sequence'], name))

    # Edges
    output.append('*arcs')
    edges = sorted(G.get_edges(), key=lambda x: x.obj_dict['sequence'])
    for edge in edges:
        attr = edge.obj_dict.get('attributes')
        if attr:
            logger.warning("Edge has attributes - don't know what to do: %s", edge.obj_dict)

        points = edge.obj_dict['points']
        assert len(points) == 2

        output.append("{} {}".format(node_map[points[0]], node_map[points[1]]))

    with open(net_f, 'w') as f:
        f.write('\n'.join(output))

    logger.info("See {}".format(net_f))
    logger.info("Recommendation: GraphInsight {}".format(net_f))


if __name__ == "__main__":
    import argparse
    import os.path

    parser = argparse.ArgumentParser(description="Convert a DOT file into a Pajek NET file")
    parser.add_argument('dotfile', help='DOT input filename')
    parser.add_argument('-v', '--verbose', action="store_true", help="Tell me what's going on")
    args = parser.parse_args()

    h1 = logging.StreamHandler(sys.stderr)
    rootLogger = logging.getLogger()
    rootLogger.addHandler(h1)
    formatter = logging.Formatter('[%(asctime)s] [%(process)s] [%(filename)s:%(lineno)s] [%(levelname)s] %(message)s')
    h1.setFormatter(formatter)

    if args.verbose:
        rootLogger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode")
    else:
        rootLogger.setLevel(logging.INFO)
        logger.debug("Run with --verbose for debug mode")

    netfile = "{}.net".format(os.path.splitext(args.dotfile)[0])
    convert(args.dotfile, netfile)
