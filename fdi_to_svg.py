"""
Convert an FDI file to an SVG

Note - this is strictly restricted to the FDI files I've been using...
"""

import svgwrite
import re
from collections import namedtuple

taxon_re = re.compile("TAXON_NAME;([^;]+);TAXON_NAME_HEIGHT;([^;]+);TAXON_NAME_COLOR;[0-9]+;TAXON_FREQUENCY;[0-9]+;TAXON_ORIG_FREQUENCY;[0-9]+;TAXON_GEOGRAPHY;;TAXON_PHENOTYPE;;TAXON_LINEAGE;;TAXON_GROUP1;Group1;;TAXON_GROUP2;Group2;;TAXON_GROUP3;Group3;;TAXON_X;([^;]+);TAXON_Y;([^;]+);TAXON_COLOR_PIE1;([^;]+);TAXON_PIE_FREQUENCY1;[0-9]+;TAXON_STYLE_PIE1;SOLID;TAXON_LINE_WIDTH;[0-9]+;TAXON_LINE_COLOR;[0-9]+;TAXON_LINE_STYLE;SOLID;TAXON_ACTIVE;TRUE")
link_re = re.compile("LINK_TAXON1;([^;]+);LINK_TAXON2;([^;]+);.*")

taxon = namedtuple('Taxon', ['name', 'size', 'x', 'y', 'colour'])


def convert(fdi_f, svg_f):
    with open(fdi_f) as f:
        in_params = True
        in_taxa = False
        in_links = False
        params = {}
        taxa = {}
        links = []
        for line in f:
            line = line.strip()
            if not line:
                continue
            print("> {}".format(line))
            if in_params:
                if line.startswith('TAXON_NAME'):
                    in_params = False
                    in_taxa = True
                else:
                    k, v = line.split(';', 1)
                    params[k] = v

            if in_taxa:
                if line.startswith('NUMBER_OF_LINKS'):
                    in_taxa = False
                    in_links = True
                    continue
                match = taxon_re.match(line)
                if not match:
                    raise ValueError("Didn't understand this line: {}".format(line))
                t = taxon(*match.groups())
                taxa[t.name] = t

            if in_links:
                if not line.startswith('LINK_TAXON'):
                    # Done
                    break

                match = link_re.match(line)
                if not match:
                    raise ValueError("Didn't understand this line: {}".format(line))
                links.append((match.group(1), match.group(2)))

    print("Taxa: {}".format(taxa))
    print("Links: {}".format(links))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert an FDI file into an SVG")
    parser.add_argument('fdifile', help='FDI input filename')
    parser.add_argument('svgfile', help='SVG output filename')
    args = parser.parse_args()

    convert(args.fdifile, args.svgfile)
