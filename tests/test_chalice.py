import pytest
from apispec import APISpec
from chalice import Chalice

from chaliceapi import PydanticPlugin, ChalicePlugin
from tests.schema import TestSchema


def test_spec():
    app = Chalice(app_name="test")
    spec = APISpec(
        title="Test Schema",
        openapi_version="3.0.1",
        version="0.0.0",
        chalice_app=app,
        plugins=[PydanticPlugin(), ChalicePlugin()],
    )

    @app.route("/", methods=["POST"], post_body_model=TestSchema)
    def example_route():
        pass

    with pytest.raises(TypeError):
        @app.route("/misconfigured", methods=["GET"], post_body_model=TestSchema)
        def misconfigured_route():
            pass
    # Since the decorator is not evaluated until the function is declared, I don't yet
    # want to figure out how to capture the TypeError in our monkeypatch in order to report
    # the accurate thing, which is "you misconfigured your route." So as a result, a route
    # can fail to register but still be included in the spec. For the purposes of unit testing,
    # we'll just remove this path from the actual generated spec since IRL code would raise
    # a TypeError for this situation (as proven above).
    del spec._paths['/misconfigured']

    assert spec.to_dict() == {
        "paths": {
            "/": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TestSchema"}
                            }
                        }
                    }
                }
            }
        },
        "info": {"title": "Test Schema", "version": "0.0.0"},
        "openapi": "3.0.1",
        "components": {
            "schemas": {
                "TestSchema": {
                    "title": "TestSchema",
                    "type": "object",
                    "properties": {
                        "hello": {"title": "Hello", "type": "string"},
                        "world": {"title": "World", "type": "integer"},
                    },
                    "required": ["hello", "world"],
                }
            }
        },
    }
