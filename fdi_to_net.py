"""
Convert an FDI file to a Pajek NET file.

Note - this is strictly restricted to the FDI files I've been using...
"""

import sys
import logging
from fdi_to_dot import parse, calc_distance


logger = logging.getLogger(__name__)


def convert(fdi_f, net_f, use_distance=False):
    params, taxa, links = parse(fdi_f)

    print(params)
    print(taxa)
    print(links)

    output = ['*Vertices {}'.format(len(taxa))]

    node_map = {}

    for i, node in enumerate(taxa):
        if node.startswith('mv '):
            label = ' '
        else:
            label = taxa[node].name.strip()
        node_map[node] = i + 1
        output.append('{} "{}"'.format(i + 1, label))

    output.append('*arcs')

    for start, end in links:
        if use_distance:
            distance = calc_distance(taxa[start].x, taxa[start].y,
                                     taxa[end].x, taxa[end].y)
            output.append("{} {} {}".format(node_map[start], node_map[end], distance))
        else:
            output.append("{} {}".format(node_map[start], node_map[end]))

    with open(net_f, 'w') as f:
        f.write('\n'.join(output))

    logger.info("See {}".format(net_f))
    logger.info("Recommendation: GraphInsight {}".format(net_f))


if __name__ == "__main__":
    import argparse
    import os.path

    parser = argparse.ArgumentParser(description="Convert an FDI file into a Pajek NET file")
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

    netfile = "{}.net".format(os.path.splitext(args.fdifile)[0])
    convert(args.fdifile, netfile, args.use_distance)
