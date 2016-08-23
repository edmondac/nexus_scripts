"""
Convert a NEXUS tree into PhyloXML (suitable for programs like Cytoscape (v2.8) with a plugin)

Uses these packages:
pip install python-nexus
pip install biopython
pip install pygraphviz
  or probably: pip install pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/"

"""

import sys
from networkx import networkx
import subprocess
import re
from tempfile import NamedTemporaryFile
from io import StringIO
from nexus import NexusReader
from Bio import Phylo
from matplotlib import pyplot as plt
plt.ion()

def _post_process_dot(dotfile):
    """
    Post-process a dot file created by networkx to make it prettier
    """
    re_node = re.compile("[^ ]+;")
    re_edge = re.compile("[^ ]+ -> [^ ]+;")

    output = []
    with open(dotfile) as df:
        for line in df:
            if re_node.match(line.strip()):
                line = line.replace(';', ' [shape=plaintext; fontsize=12; height=0.4; width=0.4; fixedsize=true];')
            elif re_edge.match(line.strip()):
                line = line.replace(';', ' [arrowsize=0.5];')
            output.append(line)

    with open(dotfile, 'w') as w:
        w.write(''.join(output))


class ConsensusTree(object):
    def __init__(self, input_file):
        self.input_file = input_file

    def draw(self):
        print("Reading {}".format(self.input_file))
        n = NexusReader(self.input_file)
        print("Found {}".format(n.taxa))
        if n.trees.ntrees != 1:
            print("I need exactly one tree... - found {}".format(n.trees.ntrees))
            sys.exit(1)

        print("Detranslating nodes")
        n.trees.detranslate()
        consensus_tree = StringIO(n.trees[0])

        print("Importing into Phylo")
        tree = Phylo.read(consensus_tree, 'newick')
        tree.ladderize()

        # This works, but isn't very pretty...
        print(Phylo.draw_ascii(tree, column_width=200))

        print("Exporting to phyloxml")
        output_file = "{}.phyloxml".format(self.input_file)
        Phylo.write(tree, output_file, 'phyloxml')

        #~ print("Converting to graph")
        #~ G = Phylo.to_networkx(tree)

        #~ print("Outputting to GraphML")
        #~ output_file = "{}.graphml".format(self.input_file)
        #~ networkx.write_graphml(G, output_file)

        # OLD THING 1
        #~ print("Drawing tree - this could take a few minutes...")
        #~ output_file = "{}.svg".format(self.input_file)
        #~ tree.ladderize()   # Flip branches so deeper clades are displayed at top
        #~ plt.figure(figsize=(24, 24))
        #~ Phylo.draw(tree)
        #~ plt.axis('off')
        #~ plt.savefig(output_file)
        #~ import pdb; pdb.set_trace()
        #~ return

        # OLD THING 2
        #~ net = Phylo.to_networkx(tree)
        #~ G = networkx.nx_agraph.to_agraph(net)
        #~ G.node_attr.update(color="red", style="filled")
        #~ G.edge_attr.update(color="blue", width="2.0")
        #~ output_file = "{}.dot".format(self.input_file)
        #~ networkx.drawing.nx_pydot.write_dot(net, output_file)
        #WARNING - this creates a .dot file but it just doesn't look like a tree!

        # dot - filter for drawing directed graphs
        # neato - filter for drawing undirected graphs
        # twopi - filter for radial layouts of graphs
        # circo - filter for circular layout of graphs
        # fdp - filter for drawing undirected graphs
        # sfdp - filter for drawing large undirected graphs
        # patchwork - filter for tree maps

        #~ G.draw(output_file, format='svg', prog='neato')


        # OLD THING 3
        #~ with NamedTemporaryFile() as dotfile:
            #~ #networkx.write_dot(net, dotfile.name)
            #~ networkx.drawing.nx_pydot.write_dot(net, dotfile.name)
            #~ _post_process_dot(dotfile.name)
            #~ subprocess.check_call(['fdp', '-Tsvg', dotfile.name, '-o', output_file])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Read a .con.tre NEXUS file and create an SVG representation of the tree")
    parser.add_argument('inputfile', help='.con.tre NEXUS file')
    args = parser.parse_args()
    t = ConsensusTree(args.inputfile)
    t.draw()
