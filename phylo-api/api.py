from flask import Blueprint, request

# Will be set in main.py
tree = None
metadata = None

tree_api = Blueprint('tree_api', __name__)


@tree_api.route("/mrca", methods=["POST"])
def run():
    mrca = tree.mrca(request.json)
    return mrca.label
