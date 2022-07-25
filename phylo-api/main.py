import argparse
import csv
import os
import treeswift


def read_tree(path):
    with open(path, 'r') as f:
        s = f.read()
        t = treeswift.read_tree_newick(s)
        for node in t.traverse_postorder():
            splits = node.label.split('|')
            if len(splits) >= 2:
                accession_parts = splits[1].split('.')
                accession_without_version = accession_parts[0]
                node.label = accession_without_version
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


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Query and calculate statistics from a phylogenetic tree')
    parser.add_argument('datadir', type=str, help='path to the data directory')
    args = parser.parse_args()
    print("Data directory: %s" % args.datadir)

    # Load data
    tree = read_tree(os.path.join(args.datadir, 'public-latest.all.nwk'))
    metadata = read_metadata(os.path.join(args.datadir, 'basic_metadata.tsv'))
