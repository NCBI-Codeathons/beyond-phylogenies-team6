from flask import Blueprint, request

tree_api = Blueprint('tree_api', __name__)


@tree_api.route("/mrca", methods=["POST"])
def run():
    print("IDs:")
    print(request.json)
    return "todo"
