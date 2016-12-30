#!/usr/bin/env python3
"""
Look through all manuscripts looking for singular readings
"""
import MySQLdb
import itertools
from collections import defaultdict

def compare_all(host, db, user, password, table, include_wits):
    """
    Connect to the mysql db and loop through what we find
    """
    if include_wits == ['all']:
        include_wits = None
        print("\nLooking for singular readings in all witnesses in db {}:{}".format(db, table))
    else:
        print("\nLooking for singular readings in {} in db {}:{}".format(', '.join(include_wits), db, table))

    db = MySQLdb.connect(host=host, user=user, passwd=password, db=db, charset='utf8')
    cur = db.cursor()

    #~ print("Setting up indexes...")
    #~ try:
        #~ cur.execute("CREATE INDEX vu_id_idx ON {}_ed_map (vu_id)".format(table))
    #~ except MySQLdb.OperationalError as e:
        #~ if "Duplicate key" not in str(e):
            #~ raise
    #~ try:
        #~ cur.execute("CREATE INDEX witness_idx ON {}_ed_map (witness(10))".format(table))
    #~ except MySQLdb.OperationalError as e:
        #~ if "Duplicate key" not in str(e):
            #~ raise
    #~ cur.execute("OPTIMIZE TABLE {}_ed_map".format(table))
    #~ print("Done")

    cur.execute("SELECT id, bv, ev, bw, ew FROM {}_ed_vus".format(table))
    vu_map = {}
    for (vu_id, bv, ev, bw, ew) in cur.fetchall():
        vu_map[vu_id] = "{}/{}-{}/{}".format(bv, bw, ev, ew)

    cur.execute("SELECT vu_id FROM {}_ed_map".format(table))
    vu_ids = sorted(set(x[0] for x in cur.fetchall()))

    sing_read_map = defaultdict(int)

    for vu in vu_ids:
        # NOTE: the GROUP_CONCAT things only make sense for count == 1...
        query = "SELECT ident, COUNT(ident) as count FROM {}_ed_map WHERE vu_id = {} GROUP BY ident".format(table, vu)
        cur.execute(query)
        singular_idents = []
        for (ident, count) in cur.fetchall():
            if count == 1:
                singular_idents.append(ident)

        for ident in singular_idents:
            query = "SELECT witness, greek FROM {}_ed_map WHERE vu_id = {} AND ident = {}".format(table, vu, ident)
            cur.execute(query)
            results = cur.fetchall()
            assert len(results) == 1
            wits, greek = results[0]
            if include_wits is None or wits in include_wits:
                print("Found singular reading: Witness {} reads {} in VU {} ({}).".format(wits, greek, vu, vu_map[vu]))
                sing_read_map[wits] += 1

    scores = sorted(set(sing_read_map.values()), reverse=True)
    for score in scores:
        print("Witnesses with {} singular readings:".format(score))
        print("\t{}".format(", ".join(x for x in sing_read_map.keys() if sing_read_map[x] == score)))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--mysql-user', required=True, help='User to connect to mysql with')
    parser.add_argument('-p', '--mysql-password', required=True, help='Password to connect to mysql with')
    parser.add_argument('-s', '--mysql-host', required=True, help='Host to connect to')
    parser.add_argument('-d', '--mysql-db', required=True, help='Database to connect to')
    parser.add_argument('-t', '--mysql-table', required=True, help='Table name to get data from')
    parser.add_argument('witness', nargs='+', help='Which witnesses to look for (can be "all")')

    args = parser.parse_args()

    compare_all(args.mysql_host,
                args.mysql_db,
                args.mysql_user,
                args.mysql_password,
                args.mysql_table,
                args.witness)
