from chalice_spec.chalice import BlueprintWithSpec

blueprint_three = BlueprintWithSpec(__name__, tags=["tag 1"])


@blueprint_three.route("/another-world-3/posts/{id}", methods=["POST"])
def the_third_blueprint_route():
    pass
