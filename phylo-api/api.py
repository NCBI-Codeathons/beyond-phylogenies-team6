from flask import Blueprint, request
from tree_utils import split_in_found_and_not_found

# Will be set in main.py
tree = None
tree_label_set = None
metadata = None

tree_api = Blueprint('tree_api', __name__)


@tree_api.route("/mrca", methods=["POST"])
def run_mrca():
    ids_found, ids_not_found = split_in_found_and_not_found(tree_label_set, request.json)
    mrca = tree.mrca(ids_found).label
    return {
        "result": mrca,
        "notFound": ids_not_found
    }


@tree_api.route("/clusters", methods=["POST"])
def run_clusters():
    seq_ids = request.json.get('ids', None)
    n_clusters = request.json.get('n_clusters', 12)
    min_rel_size = request.json.get('min_rel_size', 0.05)
    ids_found, ids_not_found = split_in_found_and_not_found(tree_label_set, seq_ids)
    if len(ids_found)>0:
        cladeness_dict = tree.clusters(ids_found, n_clusters = n_clusters, min_rel_size = min_rel_size)
    else:
        cladeness_dict = dict()
    return {
        "result": cladeness_dict,
        "notFound": ids_not_found
    }
