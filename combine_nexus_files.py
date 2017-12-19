# -*- coding: utf-8 -*-
#!/usr/bin/python

# NOTE: The '''# -*- coding: utf-8 -*-''' first line here is important as
# otherwise you get a file that MrBayes can't read properly (for some reason...)
# even though this should all be ascii......

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


template = """#nexus
BEGIN Taxa;
DIMENSIONS ntax={ntax};
TAXLABELS
{taxa}
;
END;
BEGIN Characters;
DIMENSIONS nchar={nchar};

FORMAT
    datatype=STANDARD
    missing={missing}
    gap={gap}
    symbols="{symbols}"
;
MATRIX
{matrix}
;
END;
"""

MISSING = '-'
GAP = '?'


class Nexus(object):
    def __init__(self):
        self.taxa = []
        self.symbols = []
        self.lines = {}
        self.nchar = 0

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

        self.nchar = int(match.group(3))
        self.symbols = match.group(4).split()
        print "  Loaded {} characters and {} symbols ({})".format(
            self.nchar, len(self.symbols), ', '.join(self.symbols))

        for stripe in match.group(5).splitlines():
            taxon, chars = stripe.split(' ', 1)
            assert len(chars) == self.nchar
            self.lines[taxon] = chars

        print "  Loaded matrix"

    def add_nexus(self, other_nexus):
        """
        Add data from another nexus file object to this one, creating a larger
        combined nexus file.
        """
        for t in other_nexus.taxa:
            if t not in self.taxa:
                self.taxa.append(t)

        self.symbols = sorted(set(self.symbols + other_nexus.symbols))

        self.nchar += other_nexus.nchar

        new_lines = {}

        for t in self.taxa:
            line = self.lines.get(t, MISSING * self.nchar)
            line += other_nexus.lines.get(t, MISSING * other_nexus.nchar)
            new_lines[t] = line

        self.lines = new_lines

    def write(self, output, extant_perc=0):
        """
        Write the nexus data out to a file - including only those taxa that
        are extant in extant_perc (percentage) of characters.
        """
        target_chars = self.nchar * extant_perc / 100.0
        print "Only including taxa extant in {} ({}%) of characters".format(target_chars, extant_perc)

        #self.taxa = self.taxa[:3] ## FIXME
        #self.nchar = 1000 ##FIXME

        taxa = self.taxa

        matrix = []
        for t in self.taxa:
            line = self.lines[t]
            extant = [x for x in line if x not in (MISSING, GAP)]
            if len(extant) < target_chars:
                print "Deleting {} as it's only extant in {} characters".format(t, len(extant))
                del taxa[taxa.index(t)]
                continue
            matrix.append('{} {}'.format(t, line[:self.nchar]))##FIXME

        data = template.format(ntax=len(taxa),
                               taxa='\n'.join(taxa),
                               nchar=self.nchar,
                               symbols=' '.join(self.symbols),
                               matrix='\n'.join(matrix),
                               missing=MISSING,
                               gap=GAP)
        with open(output, 'w') as f:
            f.write(unicode(data))

        print "Written combined nexus file {}".format(output)


def combine(input_files, output_file, perc):
    nex = Nexus()
    for i in input_files:
        n = Nexus()
        n.load(i)
        nex.add_nexus(n)

    nex.write(output_file, perc)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--extant_perc', default=0, type=int, help='Percentage of variant units a witness must attest to be included')
    parser.add_argument('input_file', nargs='+', help='Input nexus files')
    parser.add_argument('output_file', help='Filename to save combined nexus data to')
    args = parser.parse_args()
    combine(args.input_file, args.output_file, args.extant_perc)
