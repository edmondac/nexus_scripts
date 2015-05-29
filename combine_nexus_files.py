#!/usr/bin/python

import sys
import re

"""
Example abridged nexus file:

#nexus
BEGIN Taxa;
DIMENSIONS ntax=135;
TAXLABELS
720
020
P78
...
846
;
END;
BEGIN Characters;
DIMENSIONS nchar=210;

FORMAT
    datatype=STANDARD
    missing=-
    gap=?
    symbols=""
;
MATRIX
720 -aaaaabaaaaaa-aagaaaaaaaaaaaaaaaaaeaaaaaqaaaaaaaa---------------------------------------------------------------------------------------------------------------------------------------------------------------?-
020 paaaaabaaaaaaaaagaaaaaaaaaaaaaaaaaeaaaaanaaaaaaaaaaabaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaacaaaaaaaaaaaaaaaaaaaaaaaaaaaabgaaaaaaagaaaaaaaaaacajaaaaaaaaaaaaabaaaaacada?i
P78 -------------------------------aaadaaab-----------------abaabaaaaa----------------------------------------------------------------------------------------------------------------------------------------------?-
718 zaaaaabaaaaaaaaagaaaaaaaaaaaaaaaaaaaaaaaxaabaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabaaaaaaaaaaaaaabaaaaaaaaaaaabab----aaaaaaaaaaabacaaaaaaaaaaaaagaaabaaaaaaaaaaaaaacapaaaaaaaaaaaaabaadaacapa?a
...abaaaabcaabaaaaagaaaaaaaaaaaaaaaaaeaaaaaoaaaaaaaaaaabaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabaaaaaaaaaaaaaaaaaaacaaaaaaaaaaacaaaaaaaaaaaaaaacaaaaaaaaaaebagaaaaaaagbaaaaaaaaacajaaaacaaaaaaaabaadaaccaa?q
617 fbaaaaaaaaaaaaaagaaaaaaaaaaaaaaaaaeaaaaanaaaaaaaaaaabdaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabaaaaaaaaaaaaaaaaaaacaaaaaaaaaaacaaaaaaaaaaaaaaaaaaaaaaabaaaaaoaaaaaaagaaaaaaaaaadabaaaaaaaaaaaaabaadaaccaa?a
846 -aaaaaagabaaaaaaaaaaaaaaaaaaaaaaaaaaabaa-aaaaaaaaaaabaaaadaaaaaabacaaaaaaaaabaaaaaaaaaaaaaaaaaaacaaaaaabaaabaaabaaaaaaaaaaaaaaagaaaaabaajaaaaabaaaaaaabaaaaaaaaabaabaaacaaaaaaaaaaaaaaaagaaaahaabaaaaabaaaaaaada?l
;
END;
"""

re_nexus = re.compile(r"""#nexus
BEGIN Taxa;
DIMENSIONS ntax=([0-9]+);
TAXLABELS
(.*?)
;
END;
BEGIN Characters;
DIMENSIONS nchar=([0-9]+);

FORMAT
    datatype=STANDARD
    missing=-
    gap=\?
    symbols="(.*?)"
;
MATRIX
(.*?);
END;""", re.DOTALL)


class Nexus(object):
    def __init__(self):
        self.taxa = set()
        self.symbols = set()
        self.lines = {}

    def load(self, filename):
        """
        Load from existing nexus file
        """
        print "Loading {}".format(filename)
        with open(filename) as f:
            data = f.read()

        match = re_nexus.match(data)
        assert match, "Didn't match"
        ntax = int(match.group(1))
        taxa = match.group(2).splitlines()
        assert len(taxa) == ntax, (len(taxa), ntax)
        self.taxa = taxa
        print "  Loaded {} taxa: {}".format(ntax, ', '.join(taxa))

        nchar = int(match.group(3))
        self.symbols = match.group(4).split()
        print "  Loaded {} characters and {} symbols ({})".format(
            nchar, len(self.symbols), ', '.join(self.symbols))

        for stripe in match.group(5).splitlines():
            taxon, chars = stripe.split(' ', 1)
            assert len(chars) == nchar
            self.lines[taxon] = chars

        print "  Loaded matrix"


def combine(input_files, output_file):
    nex = []
    for i in input_files:
        n = Nexus()
        n.load(i)
        nex.append(n)

    print nex

if __name__ == "__main__":
    assert len(sys.argv) > 2, "Usage: $0 input [input] [input] output"
    combine(sys.argv[1:-1], sys.argv[-1])
