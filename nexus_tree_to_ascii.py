"""
Convert a NEXUS tree into ASCII

Uses these packages:
pip install python-nexus
pip install biopython
"""

import sys
from networkx import networkx
import subprocess
import re
from tempfile import NamedTemporaryFile
from io import StringIO
from nexus import NexusReader
from Bio import Phylo


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
        output_file = "{}.ascii".format(self.input_file)
        with open(output_file, 'w') as f:
            Phylo.draw_ascii(tree, file=f, column_width=200)

        print("See {}".format(output_file))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Read a .con.tre NEXUS file and create an ASCII representation of the tree")
    parser.add_argument('inputfile', help='.con.tre NEXUS file')
    args = parser.parse_args()
    t = ConsensusTree(args.inputfile)
    t.draw()
