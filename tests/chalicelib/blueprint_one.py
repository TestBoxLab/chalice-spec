from chalice import Blueprint

from chalice_spec import Docs
from chalice_spec.chalice import BlueprintWithSpec
from tests.schema import TestSchema

blueprint_one = BlueprintWithSpec(__name__)


@blueprint_one.route("/hello-world/deep", docs=Docs(get=TestSchema))
def the_blueprint_route():
    pass
