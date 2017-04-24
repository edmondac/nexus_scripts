"""
Convert an FDI file to a DOT file using networkx.

Note - this is strictly restricted to the FDI files I've been using...
"""

import sys
import networkx
import math
import logging
from fdi_to_svg import parse


logger = logging.getLogger(__name__)


def calc_distance(x1, y1, x2, y2):
    """
    How far between the two points?
    """
    x_delta = (x2 - x1)
    y_delta = (y2 - y1)

    return math.sqrt(x_delta ** 2 + y_delta ** 2)


def convert(fdi_f, dot_f, use_distance=False):
    params, taxa, links = parse(fdi_f)

    print(params)
    print(taxa)
    print(links)

    G = networkx.Graph()

    for node in taxa:
        if node.startswith('mv '):
            # Median vector
            colour = "red"
            size = 0.3
            label = '""'
        else:
            colour = "yellow"
            size = 0.7
            label = taxa[node].name.strip()
        G.add_node(node, color=colour, fillcolor=colour, style="filled", width=size, label=label, shape="circle")

    edges = []
    max_dist = 0
    for start, end in links:
        distance = calc_distance(taxa[start].x, taxa[start].y,
                                 taxa[end].x, taxa[end].y)
        max_dist = max(max_dist, distance)
        edges.append((start, end, distance))

    for (start, end, distance) in edges:
        if use_distance:
            if distance:
                length = 1.0 * max_dist / distance
            else:
                length = 0.1

            logger.debug("{} to {} is {}".format(taxa[start].name, taxa[end].name, distance))
            G.add_edge(start, end, len=length, label=int(distance))
        else:
            G.add_edge(start, end, label=int(distance))

    networkx.write_dot(G, dot_f)

    with open(dot_f, 'r') as f:
        dot_data = f.read()

    with open(dot_f, 'w') as f:
        # Set splines=true on the graph, to avoid edges overlapping nodes
        dot_data = dot_data.replace('{', '{\nsplines="true";\noverlap="scale";', 1)
        f.write(dot_data)

    logger.info("See {}".format(dot_f))
    logger.info("Recommendation: neato -Tsvg {} > {}.svg".format(dot_f, dot_f))

if __name__ == "__main__":
    import argparse
    import os.path

    parser = argparse.ArgumentParser(description="Convert an FDI file into an SVG")
    parser.add_argument('fdifile', help='FDI input filename')
    parser.add_argument('-v', '--verbose', action="store_true", help="Tell me what's going on")
    parser.add_argument('-d', '--use-distance', action="store_true", help="Try to use the distances in the diagram. "
                        "fdp will use them, but sometimes fails to make a good-looking network.")
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

    dotfile = "{}.dot".format(os.path.splitext(args.fdifile)[0])
    convert(args.fdifile, dotfile, args.use_distance)
