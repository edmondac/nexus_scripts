# Transform a nexus file into an RDF file

# NOTE: Network will expect amino-acid files to have a .ami extension
#       and DNA files to have an .rdf extension

# XXX: Still doesn't quite work - compare output with that of DnaSP...

import sys
from collections import OrderedDict

with open(sys.argv[1]) as f:
    data = f.readlines()

matrix = OrderedDict()

in_matrix = False
for line in data:
    line = line.strip()
    if line.lower() == 'matrix':
        in_matrix = True
        continue

    if not in_matrix:
        continue

    if ' ' not in line:
        continue

    label, stripe = line.split()
    matrix[label] = stripe

# total input characters
n_chars = len(stripe)

GAP = '-'
MISSING = '?'

print("NOTE: All characters with missing/gap will be ignored")
ignore_chars = set([])
for lab in matrix:
    for i, char in enumerate(matrix[lab]):
        if char == GAP or char == MISSING:
            ignore_chars.add(i + 1)
print("Ignoring characters: {}".format(ignore_chars))

n_included_chars = n_chars - len(ignore_chars)

output = []
n_header_lines = len(str(n_chars))
for l in range(n_header_lines):
    line = ' ' * 10
    for x in range(n_chars):
        y = x + 1  # start at 1
        if y in ignore_chars:
            continue
        y_s = str(y).ljust(n_header_lines)
        line += y_s[l]

    output.append(line)

output.extend([''] * 4)

for n, lab in enumerate(matrix):
    stripe = matrix[lab]
    output.append("H_{}{}  1".format(str(n + 1).ljust(8), ''.join(x for i, x in enumerate(stripe) if i + 1 not in ignore_chars)))
    #output.append("H_{}{}  1".format(lab.ljust(8), ''.join(x for i, x in enumerate(stripe) if i + 1 not in ignore_chars)))
    print("\t H_{} is {}".format(n + 1, lab))

output.extend([''])

output.append('10' * n_included_chars)

with open(sys.argv[2], 'w') as out:
    out.write('\n'.join(output))

print("See {}".format(sys.argv[2]))
