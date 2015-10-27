# Transform a nexus file into an RDF file

# NOTE: Network will expect amino-acid files to have a .ami extension
#       and DNA files to have an .rdf extension

from collections import OrderedDict
import json
import os


def convert(inputfile, ignore_missing):
    """
    Convert NEXUS to RDF and create a JSON mapping for use by relable_fdi.py.
    """
    with open(inputfile) as f:
        data = f.readlines()

    name = os.path.splitext(inputfile)[0]

    matrix = OrderedDict()

    in_matrix = False
    is_dna = False
    is_protien = False
    for line in data:
        if "datatype=dna" in line:
            is_dna = True
        elif "datatype=protien" in line:
            is_protien = True

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

    if not is_dna and not is_protien:
        raise ValueError("Not DNA or protien file - help!")

    if is_protien and not ignore_missing:
        print("WARNING: Amino acid file requires 'ignore-missing' - setting it now.")
        ignore_missing = True

    # total input characters
    n_chars = len(stripe)

    GAP = '-'
    MISSING = '?'

    print("NOTE: All characters with missing/gap will be ignored")
    missing_chars = set([])
    for lab in matrix:
        for i, char in enumerate(matrix[lab]):
            if char == GAP or char == MISSING:
                missing_chars.add(i + 1)
    print("Characters with GAP or MISSING: {}".format(missing_chars))

    n_included_chars = n_chars - (len(missing_chars) if ignore_missing else 0)

    output = []
    n_header_lines = len(str(n_chars))
    for l in range(n_header_lines):
        line = ' ' * 7
        for x in range(n_chars):
            y = x + 1  # start at 1
            if y in missing_chars and ignore_missing:
                continue
            y_s = str(y).ljust(n_header_lines)
            line += y_s[l]

        output.append(line)

    output.extend([''] * 4)

    mapping = {}
    for n, lab in enumerate(matrix):
        stripe = matrix[lab]
        if ignore_missing:
            stripe_s = ''.join(x for i, x in enumerate(stripe) if i + 1 not in missing_chars)
        else:
            stripe_s = ''.join(stripe)
            stripe_s = stripe_s.replace(GAP, 'N')
            stripe_s = stripe_s.replace(MISSING, 'N')
        output.append("H_{}{}  1".format(str(n + 1).ljust(5), stripe_s))
        print("\t H_{} is {}".format(n + 1, lab))
        mapping['H_{}'.format(n + 1)] = lab

    output.append('')
    output.append('1' * n_included_chars)
    output.append('')

    if is_dna:
        ext = 'rdf'
    else:
        ext = 'ami'
    outputfile = "{}.{}".format(name, ext)
    with open(outputfile, 'w') as out:
        out.write('\n'.join(output))

    mappingfile = "{}.json".format(name)
    with open(mappingfile, 'w') as m:
        json.dump(mapping, m)

    print("See {}".format(outputfile))
    print("Use {} with relable_fdi.py".format(mappingfile))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert a NEXUS file to RDF.")
    parser.add_argument('nexusfile', help='NEXUS filename')
    parser.add_argument('--ignore-missing', help='Ignore gaps and missing chars',
                        action='store_true', default=False)
    args = parser.parse_args()

    convert(args.nexusfile, args.ignore_missing)
