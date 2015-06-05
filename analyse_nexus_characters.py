#!/usr/bin/python
"""
Attempt to work out what MrBayes means when it says "There are 80 characters
incompatible with the specified coding bias. These characters will be excluded."

Assumption is that you need at least two characters each with at least two
witnesses.

However, the numbers don't quite tally with MrBayes' complaint...
"""



import sys
from collections import defaultdict


class Character(object):
    def __init__(self):
        self.readings = []

    def is_informative(self):
        # We want to count readings that occur more than once
        x = 0
        for r in set(self.readings):
            if r in ('-','?'):
                continue
            occurs = len([a for a in self.readings if a == r])
            if occurs > 1:
                print "Reading {} occurs {} times".format(r, occurs)
                x += 1

        return x > 1


def analyse(input_file):
    ntax = 0
    matrix = defaultdict(Character)

    with open(input_file) as nexus:
        in_matrix = False
        for line in nexus:
            # Look for the matrix
            if in_matrix is False:
                if line.strip() == "MATRIX":
                    in_matrix = True
                continue

            # We're in the matrix
            if line.strip() == ';':
                break
            taxon, states = line.split()
            ntax += 1
            for i, s in enumerate(states):
                matrix[i].readings.append(s)

    inf = 0
    notinf = 0
    for char in matrix.values():
        if char.is_informative():
            inf += 1
        else:
            notinf += 1

    print "Matrix has {} taxa and {} characters".format(ntax, len(matrix))
    print "  {} characters are informative".format(inf)
    print "  {} characters are uninformative".format(notinf)


if __name__ == "__main__":
    nexus = sys.argv[1]
    analyse(nexus)
