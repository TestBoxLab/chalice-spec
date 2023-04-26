from chalice_spec.chalice import BlueprintWithSpec

blueprint_three = BlueprintWithSpec(__name__, generate_default_docs=True)


@blueprint_three.route("/another-world-3/post", methods=["POST"])
def the_third_blueprint_route():
    pass
