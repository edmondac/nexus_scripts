"""
Convert an FDI file to an SVG

Note - this is strictly restricted to the FDI files I've been using...
"""

import svgwrite
from svgwrite import cm, mm
import re
from collections import namedtuple

taxon_re = re.compile("TAXON_NAME;([^;]+);TAXON_NAME_HEIGHT;([^;]+);TAXON_NAME_COLOR;[0-9]+;TAXON_FREQUENCY;[0-9]+;TAXON_ORIG_FREQUENCY;[0-9]+;TAXON_GEOGRAPHY;;TAXON_PHENOTYPE;;TAXON_LINEAGE;;TAXON_GROUP1;Group1;;TAXON_GROUP2;Group2;;TAXON_GROUP3;Group3;;TAXON_X;([^;]+);TAXON_Y;([^;]+);TAXON_COLOR_PIE1;([^;]+);TAXON_PIE_FREQUENCY1;[0-9]+;TAXON_STYLE_PIE1;SOLID;TAXON_LINE_WIDTH;[0-9]+;TAXON_LINE_COLOR;[0-9]+;TAXON_LINE_STYLE;SOLID;TAXON_ACTIVE;TRUE")
link_re = re.compile("LINK_TAXON1;([^;]+);LINK_TAXON2;([^;]+);.*")

taxon = namedtuple('Taxon', ['name', 'fontsize', 'x', 'y', 'colour'])

colmap = {'65535': 'yellow',
          '255': 'red'}


def parse(fdi_f):
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
                name, fontsize, x, y, colour = match.groups()
                t = taxon(name, int(fontsize), int(x), int(y), colmap[colour])
                taxa[t.name] = t

            if in_links:
                if not line.startswith('LINK_TAXON'):
                    # Done
                    break

                match = link_re.match(line)
                if not match:
                    raise ValueError("Didn't understand this line: {}".format(line))
                links.append((match.group(1), match.group(2)))

    #~ print("Taxa: {}".format(taxa))
    #~ print("Links: {}".format(links))
    return params, taxa, links


def convert(fdi_f, svg_f):
    params, taxa, links = parse(fdi_f)

    min_x = 10e10
    max_x = 0
    min_y = 10e10
    max_y = 0
    for t in taxa.values():
        if t.x > max_x:
            max_x = t.x
        if t.y > max_y:
            max_y = t.y
        if t.x < min_x:
            min_x = t.x
        if t.y < min_y:
            min_y = t.y

    size_x = max_x - min_x
    size_y = max_y - min_y

    padding = size_x * 0.1

    offset_x = padding // 2 - min_x
    offset_y = padding // 2 - min_y

    sizemult = size_x / 600.0
    print("Magic size multiplication faction: {}".format(sizemult))


    print(str((min_x, max_x, min_y, max_y)))

    dwg = svgwrite.Drawing(filename=svg_f, size=(size_x + padding, size_y + padding))

    for start, end in links:
        line = svgwrite.shapes.Line(start=(taxa[start].x + offset_x, taxa[start].y + offset_y),
                                    end=(taxa[end].x + offset_x, taxa[end].y + offset_y),
                                    stroke='#333333')
        dwg.add(line)

    for t in taxa.values():
        if t.name.startswith('mv'):
            # median vector
            radius = int(int(params['MED_RADIUS']) * sizemult)
        else:
            radius = int(int(params['MIN_CIRC_RADIUS']) * sizemult)

        g = svgwrite.container.Group()
        circle = svgwrite.shapes.Circle(center=(t.x + offset_x, t.y + offset_y),
                                        r=radius + 1,
                                        fill='black')
        g.add(circle)
        innercircle = svgwrite.shapes.Circle(center=(t.x + offset_x, t.y + offset_y),
                                             r=radius,
                                             fill=t.colour)
        g.add(innercircle)
        if not t.name.startswith('mv'):
            t = svgwrite.text.Text(t.name.strip(),
                                   x=[t.x + offset_x + radius * 2],
                                   y=[t.y + offset_y],
                                   font_size=int(t.fontsize * sizemult),
                                   font_family='ariel')
            g.add(t)
        dwg.add(g)

    dwg.save()
    print("\nWritten {}".format(svg_f))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert an FDI file into an SVG")
    parser.add_argument('fdifile', help='FDI input filename')
    parser.add_argument('svgfile', help='SVG output filename')
    args = parser.parse_args()

    convert(args.fdifile, args.svgfile)
