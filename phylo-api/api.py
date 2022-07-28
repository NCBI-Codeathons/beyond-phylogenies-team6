from flask import Blueprint, request
from tree_utils import split_in_found_and_not_found

# Will be set in main.py
tree = None
metadata = None

tree_api = Blueprint('tree_api', __name__)


def get_filter_criteria(param_dict):
    filter_criteria = dict()
    filter_criteria["date_from"] = param_dict.get('date_from', None)
    filter_criteria["date_to"] = param_dict.get('date_to', None)
    filter_criteria["country"] = param_dict.get('country', None)
    filter_criteria["region"] = param_dict.get('region', None)
    filter_criteria = {k:v for k, v in filter_criteria.items() if v is not None}
    if len(filter_criteria) == 0: filter_criteria = None
    return filter_criteria


@tree_api.route("/mrca", methods=["POST"])
def run_mrca():
    seq_ids = request.json.get('ids', None)
    filter_criteria = get_filter_criteria(request.json)
    
    ids_found, ids_not_found = split_in_found_and_not_found(tree.node_lookup.keys(), seq_ids)
    mrca_label, cladeness = tree.cladeness(ids_found,
                                           metadata = metadata,
                                           filter_criteria = filter_criteria)
    return {
        "result": cladeness,
        "notFound": ids_not_found
    }


@tree_api.route("/clusters", methods=["POST"])
def run_clusters():
    seq_ids = request.json.get('ids', None)
    n_clusters = request.json.get('n_clusters', 12)
    min_rel_size = request.json.get('min_rel_size', 0.05)
    filter_criteria = get_filter_criteria(request.json)
    
    ids_found, ids_not_found = split_in_found_and_not_found(tree.node_lookup.keys(), seq_ids)
    if len(ids_found)>0:
        cladeness_dict = tree.clusters(ids_found,
                                       n_clusters = n_clusters,
                                       min_rel_size = min_rel_size,
                                       metadata = metadata,
                                       filter_criteria = filter_criteria)
    else:
        cladeness_dict = dict()
    return {
        "result": cladeness_dict,
        "notFound": ids_not_found
    }
