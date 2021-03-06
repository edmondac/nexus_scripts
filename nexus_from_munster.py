# -*- coding: utf-8 -*-
import sys
import string
import MySQLdb

MISSING = "-"
GAP = "?"

_possible_symbols = list(string.ascii_letters) + list(string.digits)
_sym_map = {}


def get_symbol(x):
    """
    Return an appropriate symbol to use for MyBayes, always returning the
    same symbol for the same input.
    """
    if x in _sym_map:
        return _sym_map[x]
    else:
        sym = _possible_symbols.pop(0)
        _sym_map[x] = sym
        return sym


def nexus(host, db, user, password, table, book, perc, filename):
    """
    Connect to the mysql db and loop through what we find
    """
    db = MySQLdb.connect(host=host, user=user, passwd=password, db=db, charset='utf8')
    cur = db.cursor()

    if book:
        cur.execute("SELECT id FROM {}_ed_vus WHERE BOOK=%s ORDER BY id".format(table), (book, ))
    else:
        cur.execute("SELECT id FROM {}_ed_vus ORDER BY id".format(table))
    vus = sorted([x[0] for x in cur.fetchall()])
    target = len(vus) * perc / 100.0
    print("Including only witnesses extant in {} ({}%) variant units".format(target, perc))

    cur.execute("SELECT DISTINCT(witness) FROM {}_ed_map".format(table))
    witnesses = [x[0] for x in cur.fetchall()]

    symbols = set()
    matrix = []
    print()
    witnesses_copy = witnesses[:]
    for i, wit in enumerate(witnesses_copy):
        sys.stdout.write("\r{}/{}: {}    ".format(i + 1, len(witnesses_copy), wit))
        sys.stdout.flush()

        cur.execute("SELECT vu_id, ident FROM {}_ed_map WHERE witness = %s".format(table),
                    (wit, ))
        wit_map = {}
        for row in cur.fetchall():
            ident = row[1]
            # zw: the textual evidence does not allow to cite the witness for
            # only one of the variants (equivalent of the double arrow in the
            # ECM apparatus).
            # zz: lacuna
            if ident in ('zw', 'zz'):
                label = MISSING
            else:
                label = get_symbol(ident)
                symbols.add(label)

            wit_map[row[0]] = label

        stripe = []
        for vu in vus:
            stripe.append(wit_map.get(vu, GAP))

        this_count = len([x for x in stripe if x not in (GAP, MISSING)])
        if this_count > target:
            matrix.append("{} {}".format(wit, ''.join(stripe)))
        else:
            print("Deleting witness {} - it is only extant in {} variant unit(s)".format(wit, this_count))
            del witnesses[witnesses.index(wit)]

    nexus_data = """#nexus
BEGIN Taxa;
DIMENSIONS ntax={};
TAXLABELS
{}
;
END;
BEGIN Characters;
DIMENSIONS nchar={};

FORMAT
    datatype=STANDARD
    missing={}
    gap={}
    symbols="{}"
;
MATRIX
{}
;
END;
""".format(len(witnesses),
           "\n".join(witnesses),
           len(vus),
           MISSING,
           GAP,
           ' '.join(sorted(list(symbols))),
           '\n'.join(matrix))

    with open(filename, 'w') as fh:
        fh.write(nexus_data)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--mysql-user', required=True, help='User to connect to mysql with')
    parser.add_argument('-p', '--mysql-password', required=True, help='Password to connect to mysql with')
    parser.add_argument('-s', '--mysql-host', required=True, help='Host to connect to')
    parser.add_argument('-d', '--mysql-db', required=True, help='Database to connect to')
    parser.add_argument('-t', '--table', required=True, help='Table name to get data from')
    parser.add_argument('-b', '--book', default=0, type=int, help='Restrict to the specified book number')
    parser.add_argument('-e', '--extant_perc', default=0, type=int, help='Percentage of variant units a witness must attest to be included')
    parser.add_argument('output_file', help='Filename to save nexus data to')
    args = parser.parse_args()

    nexus(args.mysql_host,
          args.mysql_db,
          args.mysql_user,
          args.mysql_password,
          args.table,
          args.book,
          args.extant_perc,
          args.output_file)
    print()

if __name__ == "__main__":
    main()
