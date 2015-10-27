#!/usr/bin/env python

DNA = 'ACTG'
PROTIEN = 'FSTKEYVQMCLAWPHDRIG'  # Amino acids... NOTE: We miss out 'N' because Network.exe gets confused by it...


def subset(input_file, output_file, taxa, trans):
    """
    Create a subset of the supplied nexus file using only the listed taxa.

    @param input_file: filename of original nexus file
    @param output_file: filename for new nexus file
    @param taxa: list of taxa to include
    @param trans: characters to transform into

    Constant characters are removed.
    """
    with open(input_file) as f:
        data = f.read()

    in_m = False
    stripes = {}
    for line in data.splitlines():
        if in_m and ' ' in line:
            n, chars = line.split()
            if n not in taxa:
                continue
            stripes[n] = chars

        if line.strip() == 'MATRIX':
            in_m = True

    keep = []
    convs = {}
    for i, a in enumerate(list(stripes.values())[0]):
        col = set()
        for k in stripes:
            col.add(stripes[k][i])
        if len(list(col)) != 1:
            keep.append(i)

        col_conv = {}

        # Transform
        if len([a for a in col if a not in ('-', '?')]) > len(trans):
            raise ValueError("More than {} character states - cannot do transform".format(len(trans)))
        use = list(tuple(trans))
        for s in col:
            if s in ('-', '?'):
                col_conv[s] = s
            else:
                col_conv[s] = use.pop(0)
        convs[i] = col_conv

    if trans == DNA:
        trans_name = 'dna'
    elif trans == PROTIEN:
        trans_name = 'protien'
    else:
        trans_name = 'standard'

    with open(output_file, 'w') as output:
        # header
        output.write("""#NEXUS
begin data;
dimensions ntax={} nchar={};
format missing=? gap=- matchchar=. datatype={};
matrix
""".format(len(taxa), len(keep), trans_name))
        for k in stripes:
            output.write("{} ".format(k))
            for i in keep:
                output.write(convs[i][stripes[k][i]])
            output.write('\n')

        output.write(";\nEND;\n")

    print("File {} written".format(output))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create subset of a nexus file.")
    parser.add_argument('-d', '--dna-transform', action="store_true", default=False,
                        help='Transform the data into DNA labels (ACTG)')
    parser.add_argument('-a', '--amino-acid-transform', action="store_true", default=False,
                        help='Transform the data into protien labels (FSTKEYVQMCLAWPHDRIG)')  # NOTE: We miss out 'N' because Network.exe gets confused by it...
    parser.add_argument('-i', '--input-file',
                        help='Input filename')
    parser.add_argument('-o', '--output-file',
                        help='Output filename')
    parser.add_argument('taxon', nargs='+',
                        help="Taxa to include")
    args = parser.parse_args()

    transform = None
    if args.dna_transform:
        transform = DNA
    elif args.amino_acid_transform:
        transform = PROTIEN

    if not transform:
        print("Please specify -a or -d")
        raise SystemExit(1)

    subset(args.input_file, args.output_file, args.taxon, transform)
