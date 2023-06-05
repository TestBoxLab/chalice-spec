from apispec import APISpec

from chalice_spec import PydanticPlugin
from chalice_spec.chalice import ChaliceWithSpec


def setup_test(generate_default_docs=False):
    spec = APISpec(
        title="Test Schema",
        openapi_version="3.0.1",
        version="0.0.0",
        plugins=[PydanticPlugin()],
    )
    app = ChaliceWithSpec(
        app_name="test", spec=spec, generate_default_docs=generate_default_docs
    )
    return app, spec


def test_blueprint_one():
    from .chalicelib.blueprint_one import blueprint_one

    app, spec = setup_test()
    app.register_blueprint(blueprint_one, url_prefix="/prefix")

    assert spec.to_dict() == {
        "paths": {
            "/prefix/hello-world/deep": {
                "get": {
                    "tags": ["/prefix"],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TestSchema"
                                    }
                                }
                            },
                        }
                    },
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


def test_blueprint_two():
    from .chalicelib.blueprint_two import blueprint_two

    app, spec = setup_test()
    app.register_blueprint(blueprint_two)

    assert spec.to_dict() == {
        "paths": {
            "/another-world/post": {
                "post": {
                    "tags": ["/another-world"],
                    "summary": "this is a docstring",
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TestSchema"
                                    }
                                }
                            },
                        }
                    },
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


def test_blueprint_three_no_default_docs():
    from .chalicelib.blueprint_three import blueprint_three

    app, spec = setup_test(generate_default_docs=False)
    app.register_blueprint(blueprint_three)
    assert spec.to_dict() == {
        "paths": {},
        "info": {"title": "Test Schema", "version": "0.0.0"},
        "openapi": "3.0.1",
    }


def test_blueprint_three_with_default_docs():
    from .chalicelib.blueprint_three import blueprint_three

    app, spec = setup_test(generate_default_docs=True)
    app.register_blueprint(blueprint_three)
    assert spec.to_dict() == {
        "paths": {
            "/another-world-3/posts/{id}": {
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "post": {
                    "tags": ["tag 1"],
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {"$ref": "#/components/schemas/BaseModel"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/BaseModel"}
                                }
                            },
                        }
                    },
                },
            }
        },
        "info": {"title": "Test Schema", "version": "0.0.0"},
        "openapi": "3.0.1",
        "components": {
            "schemas": {
                "BaseModel": {"title": "BaseModel", "type": "object", "properties": {}}
            }
        },
    }


def test_two_blueprints():
    app, spec = setup_test()

    from .chalicelib.blueprint_one import blueprint_one
    from .chalicelib.blueprint_two import blueprint_two

    app.register_blueprint(blueprint_one, url_prefix="/prefixed")
    app.register_blueprint(blueprint_two)

    assert spec.to_dict() == {
        "paths": {
            "/prefixed/hello-world/deep": {
                "get": {
                    "tags": ["/prefixed"],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TestSchema"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/another-world/post": {
                "post": {
                    "summary": "this is a docstring",
                    "tags": ["/another-world"],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TestSchema"
                                    }
                                }
                            },
                        }
                    },
                }
            },
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
