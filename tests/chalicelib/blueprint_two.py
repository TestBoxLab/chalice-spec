from chalice_spec import Docs
from chalice_spec.chalice import BlueprintWithSpec
from tests.schema import TestSchema

blueprint_two = BlueprintWithSpec(__name__)


@blueprint_two.route(
    "/another-world/post", docs=Docs(post=TestSchema), methods=["POST"]
)
def the_second_blueprint_route():
    """this is a docstring"""
    pass
