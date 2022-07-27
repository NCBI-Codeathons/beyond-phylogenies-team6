from flask import Blueprint, request

# Will be set in main.py
tree = None
metadata = None

tree_api = Blueprint('tree_api', __name__)


@tree_api.route("/mrca", methods=["POST"])
def run_mrca():
    mrca = tree.mrca(request.json).label
    return mrca


@tree_api.route("/cladeness", methods=["POST"])
def run_hierarchical():
    cladeness_dict = tree.cladeness(request.json)
    return cladeness_dict
