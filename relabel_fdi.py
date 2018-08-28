import json

def relabel(fdi, js):
    with open(js) as f:
        mapping = json.load(f)
    with open(fdi) as x:
        data = x.read()

    # Loop through from the longest to the shortest, so things like H_1 don't
    # mess up H_10...
    keys = reversed(sorted(mapping.keys(), key=len))
    for k in keys:
        print("Replacing {} with {}".format(k, mapping[k]))
        data = data.replace(k, mapping[k])

    with open(fdi, 'w') as f:
        f.write(data)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Relable an FDI file putting real manuscript names back in")
    parser.add_argument('fdifile', help='FDI filename')
    parser.add_argument('jsonfile', help='JSON mapping filename')
    args = parser.parse_args()

    relabel(args.fdifile, args.jsonfile)
