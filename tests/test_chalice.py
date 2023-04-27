import pytest
from apispec import APISpec

from chalice_spec.chalice import ChaliceWithSpec
from chalice_spec.docs import Docs, Resp, Op
from chalice_spec.pydantic import PydanticPlugin
from tests.schema import TestSchema, AnotherSchema


def setup_test():
    spec = APISpec(
        title="Test Schema",
        openapi_version="3.0.1",
        version="0.0.0",
        plugins=[PydanticPlugin()],
    )
    app = ChaliceWithSpec(app_name="test", spec=spec)
    return app, spec


# Test 1: make sure that this still works as-is.
def test_nothing():
    app, spec = setup_test()

    @app.route("/", methods=["GET"])
    def example_route():
        pass


# Test 2: test that we can get a response spec from only a model
def test_response_spec():
    app, spec = setup_test()

    @app.route(
        "/",
        methods=["GET"],
        docs=Docs(
            get=TestSchema,
        ),
    )
    def test():
        pass

    assert spec.to_dict() == {
        "paths": {
            "/": {
                "get": {
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
                    "tags": ["/"],
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


# Test 3: test that we can get a response and request spec from only models
def test_request_response_spec():
    app, spec = setup_test()

    @app.route(
        "/test",
        methods=["GET", "POST"],
        docs=Docs(
            post=Op(
                request=TestSchema,
                response=AnotherSchema,
            )
        ),
    )
    def test():
        pass

    assert spec.to_dict() == {
        "paths": {
            "/test": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TestSchema"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/AnotherSchema"
                                    }
                                }
                            },
                        }
                    },
                    "tags": ["/test"],
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
                },
                "AnotherSchema": {
                    "title": "AnotherSchema",
                    "type": "object",
                    "properties": {
                        "nintendo": {"title": "Nintendo", "type": "string"},
                        "atari": {"title": "Atari", "type": "string"},
                    },
                    "required": ["nintendo", "atari"],
                },
            }
        },
    }


# Test 4: test that we can get a single response and request spec from a full Operation
def test_operation():
    app, spec = setup_test()

    @app.route(
        "/ops",
        methods=["GET", "POST"],
        docs=Docs(
            post=Op(
                request=AnotherSchema,
                response=Resp(
                    code=201, description="Updated successfully!", model=TestSchema
                ),
            )
        ),
    )
    def test():
        pass

    assert spec.to_dict() == {
        "paths": {
            "/ops": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AnotherSchema"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Updated successfully!",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TestSchema"
                                    }
                                }
                            },
                        }
                    },
                    "tags": ["/ops"],
                }
            }
        },
        "info": {"title": "Test Schema", "version": "0.0.0"},
        "openapi": "3.0.1",
        "components": {
            "schemas": {
                "AnotherSchema": {
                    "title": "AnotherSchema",
                    "type": "object",
                    "properties": {
                        "nintendo": {"title": "Nintendo", "type": "string"},
                        "atari": {"title": "Atari", "type": "string"},
                    },
                    "required": ["nintendo", "atari"],
                },
                "TestSchema": {
                    "title": "TestSchema",
                    "type": "object",
                    "properties": {
                        "hello": {"title": "Hello", "type": "string"},
                        "world": {"title": "World", "type": "integer"},
                    },
                    "required": ["hello", "world"],
                },
            }
        },
    }


# Test 5: test that we can get summaries
def test_summaries():
    app, spec = setup_test()

    @app.route(
        "/summaries",
        methods=["GET"],
        docs=Docs(
            summary="This is a summary of an API request.",
        ),
    )
    def summary():
        pass

    assert spec.to_dict() == {
        "paths": {"/summaries": {"summary": "This is a summary of an API request."}},
        "info": {"title": "Test Schema", "version": "0.0.0"},
        "openapi": "3.0.1",
    }


# Test 6: test shorthand
def test_shorthand():
    app, spec = setup_test()

    @app.route(
        "/", methods=["POST"], docs=Docs(request=TestSchema, response=AnotherSchema)
    )
    def post():
        pass

    @app.route(
        "/", methods=["PUT"], docs=Docs(request=AnotherSchema, response=TestSchema)
    )
    def put():
        pass

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
                    },
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/AnotherSchema"
                                    }
                                }
                            },
                        }
                    },
                    "tags": ["/"],
                },
                "put": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AnotherSchema"}
                            }
                        }
                    },
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
                    "tags": ["/"],
                },
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
                },
                "AnotherSchema": {
                    "title": "AnotherSchema",
                    "type": "object",
                    "properties": {
                        "nintendo": {"title": "Nintendo", "type": "string"},
                        "atari": {"title": "Atari", "type": "string"},
                    },
                    "required": ["nintendo", "atari"],
                },
            }
        },
    }


# Test 7: test for contract violations
def test_contract_violations():
    app, spec = setup_test()

    with pytest.raises(TypeError):

        @app.route("/", methods=["GET", "POST"], docs=Docs(request=TestSchema))
        def test():
            pass

    with pytest.raises(TypeError):

        @app.route("/", methods=["GET"], docs=Docs(request=TestSchema, get=Op()))
        def test():
            pass

    with pytest.raises(TypeError):
        Op(response=Resp(model=TestSchema), responses=[Resp(model=TestSchema)])

    with pytest.raises(TypeError):
        Op(
            responses=[
                Resp(code=200, model=AnotherSchema),
                Resp(code=200, model=TestSchema),
            ]
        )


# Test 8: setting up parameters for the endpoint
def test_parameters():
    app, spec = setup_test()

    @app.route(
        "/post/{id}",
        methods=["GET"],
        docs=Docs(response=AnotherSchema),
    )
    def get_post():
        pass

    assert spec.to_dict() == {
        "paths": {
            "/post/{id}": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/AnotherSchema"
                                    }
                                }
                            },
                        }
                    },
                    "tags": ["/post"],
                },
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {"type": "string"},
                        "required": True,
                    }
                ],
            }
        },
        "info": {"title": "Test Schema", "version": "0.0.0"},
        "openapi": "3.0.1",
        "components": {
            "schemas": {
                "AnotherSchema": {
                    "title": "AnotherSchema",
                    "type": "object",
                    "properties": {
                        "nintendo": {"title": "Nintendo", "type": "string"},
                        "atari": {"title": "Atari", "type": "string"},
                    },
                    "required": ["nintendo", "atari"],
                }
            }
        },
    }


# Test 9: different content_types
def test_content_types():
    app, spec = setup_test()

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["multipart/form-data"],
        docs=Docs(request=TestSchema, response=AnotherSchema),
    )
    def get_post():
        pass

    assert spec.to_dict() == {
        "paths": {
            "/posts": {
                "post": {
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {"$ref": "#/components/schemas/TestSchema"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/AnotherSchema"
                                    }
                                }
                            },
                        }
                    },
                    "tags": ["/posts"],
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
                },
                "AnotherSchema": {
                    "title": "AnotherSchema",
                    "type": "object",
                    "properties": {
                        "nintendo": {"title": "Nintendo", "type": "string"},
                        "atari": {"title": "Atari", "type": "string"},
                    },
                    "required": ["nintendo", "atari"],
                },
            }
        },
    }


def test_content_types_with_operation():
    app, spec = setup_test()

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["multipart/form-data"],
        docs=Docs(post=Op(request=TestSchema, response=AnotherSchema)),
    )
    def get_post():
        pass

    assert spec.to_dict() == {
        "paths": {
            "/posts": {
                "post": {
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {"$ref": "#/components/schemas/TestSchema"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/AnotherSchema"
                                    }
                                }
                            },
                        }
                    },
                    "tags": ["/posts"],
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
                },
                "AnotherSchema": {
                    "title": "AnotherSchema",
                    "type": "object",
                    "properties": {
                        "nintendo": {"title": "Nintendo", "type": "string"},
                        "atari": {"title": "Atari", "type": "string"},
                    },
                    "required": ["nintendo", "atari"],
                },
            }
        },
    }
