#!/usr/bin/env python

DNA = 'ACTG'
PROTIEN = 'FSTKEYVQMCLAWPHDRIG'  # Amino acids... NOTE: We miss out 'N' because Network.exe gets confused by it...


def subset(input_file, output_file, taxa, trans, frag_perc, skip_complex_characters=False):
    """
    Create a subset of the supplied nexus file using only the listed taxa.

    @param input_file: filename of original nexus file
    @param output_file: filename for new nexus file
    @param taxa: list of taxa to include
    @param trans: characters to transform into
    @param frag_perc: (int) fragmentation percentage above which witnesses are excluded
    @param skip_complex_characters: (bool) skip characters with too many states for the chosen encoding

    Constant characters are removed.
    """
    with open(input_file) as f:
        data = f.read()

    auto_taxa = False
    if taxa == ['all']:
        print("Using all taxa found in input file")
        auto_taxa = True
        taxa = []

    in_m = False
    stripes = {}
    for line in data.splitlines():
        if in_m and ' ' in line:
            n, chars = line.split()
            total_chars = len(chars)
            missing_chars = chars.count('?') + chars.count('-')
            my_frag_perc = (missing_chars * 100.0 / total_chars)
            if my_frag_perc > frag_perc:
                print("{} is {} fragmented - excluding it"
                      .format(n, my_frag_perc))
                continue

            if auto_taxa:
                taxa.append(n)
            elif n not in taxa:
                continue

            stripes[n] = chars

        if line.strip().upper() == 'MATRIX':
            in_m = True

    assert stripes, stripes

    keep = []
    convs = {}
    complex_chars = []
    for i, a in enumerate(list(stripes.values())[0]):
        col = set()
        for k in stripes:
            col.add(stripes[k][i])
        if len(list(col)) != 1:
            keep.append(i)

        col_conv = {}

        if trans:
            # Transform
            n_states = len([a for a in col if a not in ('-', '?')])
            if n_states > len(trans):
                if skip_complex_characters:
                    print("Character has {} character states - skipping".format(n_states))
                    complex_chars.append(i)
                    continue
                else:
                    raise ValueError("More than {} character states ({}) - cannot do transform"
                                     .format(len(trans), n_states))
            use = list(tuple(trans))

        for s in col:
            if trans:
                if s in ('-', '?'):
                    col_conv[s] = s
                else:
                    col_conv[s] = use.pop(0)
            else:
                col_conv[s] = s

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
                if i not in complex_chars:
                    assert i in convs
                    output.write(convs[i][stripes[k][i]])
            output.write('\n')

        output.write(";\nEND;\n")

    if complex_chars:
        print("WARNING: Skipped {} characters as they were too complex for the encoding".format(len(complex_chars)))
    print("File {} written".format(output))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create subset of a nexus file.")
    parser.add_argument('-d', '--dna-transform', action="store_true", default=False,
                        help='Transform the data into DNA labels (ACTG)')
    parser.add_argument('-a', '--amino-acid-transform', action="store_true", default=False,
                        help='Transform the data into protien labels (FSTKEYVQMCLAWPHDRIG)')  # NOTE: We miss out 'N' because Network.exe gets confused by it...
    parser.add_argument('-f', '--fragmentation-level', default=25, type=int,
                        help='Acceptable fragmentation level (percentage) above which witnesses will be excluded')
    parser.add_argument('-i', '--input-file',
                        help='Input filename')
    parser.add_argument('-o', '--output-file',
                        help='Output filename')
    parser.add_argument('taxon', nargs='+',
                        help="Taxa to include (can be 'all')")
    parser.add_argument('--ignore-too-many-character-states', default=False, action='store_true',
                        help="For characters with too many states for the encoding, just ignore them. Default is to abort.")
    args = parser.parse_args()

    transform = None
    if args.dna_transform:
        transform = DNA
    elif args.amino_acid_transform:
        transform = PROTIEN

    if not transform:
        print("Not transforming symbols - see -a or -d for details")

    subset(args.input_file, args.output_file, args.taxon, transform, args.fragmentation_level,
           args.ignore_too_many_character_states)
