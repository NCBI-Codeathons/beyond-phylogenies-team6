import argparse
import csv
import os
import pickle
from flask import Flask
import api
from api import tree_api
import re

from tree_statistics import *

def read_tree(path):
    with open(path, 'r') as f:
        s = f.read()
        t = treeswift.read_tree_newick(s)
        for node in t.traverse_postorder(leaves = True, internal = False):
            splits = node.label.split('|')
            found_accession = False
            for s in splits:
                if not re.match(r"^\d{4}-\d{2}-\d{2}$",s) and "/" not in s:
                    accession_parts = s.split('.')
                    accession_without_version = accession_parts[0]
                    node.label = accession_without_version
                    found_accession = True
                    break
            if not found_accession:
                node.label = "unknown"
        t = t.extract_tree_without(["unknown"])
        return t


def read_metadata(path):
    metadata = {}
    with open(path) as f:
        tsv = csv.DictReader(f, delimiter='\t')
        for line in tsv:
            metadata[line['genbank_accession']] = {
                'region': line['region'],
                'country': line['country'],
                'date': line['date']
            }
    return metadata


app = Flask(__name__)
app.register_blueprint(tree_api)


if __name__ == '__main__':  # If the program is directly called from the CLI
    # Parse arguments
    parser = argparse.ArgumentParser(description='Query and calculate statistics from a phylogenetic tree')
    parser.add_argument('datadir', type=str, help='path to the data directory')
    args = parser.parse_args()
    datadir = args.datadir
else:  # Defaults for the Docker container
    datadir = '/data'

print("Data directory: %s" % datadir)


# Load data
if os.path.exists(os.path.join(datadir, 'public-latest.all.p')):
    print("Loading tree from pickle file.")
    tree = pickle.load(open(os.path.join(datadir, 'public-latest.all.p'), "rb"))
else:
    print("Loading tree from newick file.")
    tree = read_tree(os.path.join(datadir, 'public-latest.all.nwk'))
    print("Saving tree as pickle file for faster loading next time.")
    pickle.dump(tree, open(os.path.join(datadir, 'public-latest.all.p'), "wb" ))
tree = enhance_swift_tree(tree)
print("Loading metadata.")
metadata = read_metadata(os.path.join(datadir, 'basic_metadata.tsv'))

# Pass data to API
api.tree = tree
api.metadata = metadata

print("Starting app.")

if __name__ == '__main__':
    # Start API
    app.run(host='0.0.0.0', port=2507)
