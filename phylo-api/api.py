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


@tree_api.route("/cladeness", methods=["POST"])
def run_hierarchical():
    ids_found, ids_not_found = split_in_found_and_not_found(tree_label_set, request.json)
    cladeness_dict = tree.cladeness(ids_found)
    return {
        "result": cladeness_dict,
        "notFound": ids_not_found
    }
