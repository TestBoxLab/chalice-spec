from apispec import APISpec

from chalice_spec.pydantic import PydanticPlugin
from tests.schema import TestSchema, NestedSchema


def test_pydantic():
    spec = APISpec(
        title="Test Schema",
        openapi_version="3.0.1",
        version="0.0.0",
        plugins=[PydanticPlugin()],
    )
    spec.components.schema("TestSchema", model=TestSchema)

    assert spec.to_dict() == {
        "paths": {},
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


def test_deeply_nested_schemas():
    spec = APISpec(
        title="Test Schema",
        openapi_version="3.0.1",
        version="0.0.0",
        plugins=[PydanticPlugin()],
    )
    spec.components.schema("NestedSchema", model=NestedSchema, spec=spec)

    assert spec.to_dict() == {
        "paths": {},
        "info": {"title": "Test Schema", "version": "0.0.0"},
        "openapi": "3.0.1",
        "components": {
            "schemas": {
                "NestedSchema": {
                    "title": "NestedSchema",
                    "type": "object",
                    "properties": {
                        "hello": {"title": "Hello", "type": "string"},
                        "deeply": {"$ref": "#/components/schemas/DeeplyNestedSchema"},
                    },
                    "required": ["hello", "deeply"],
                },
                "DeeplyNestedSchema": {
                    "title": "DeeplyNestedSchema",
                    "type": "object",
                    "properties": {
                        "more_deeply": {
                            "$ref": "#/components/schemas/MoreDeeplyNestedSchema"
                        },
                    },
                    "required": ["more_deeply"],
                },
                "MoreDeeplyNestedSchema": {
                    "title": "MoreDeeplyNestedSchema",
                    "type": "object",
                    "properties": {
                        "base_type": {"title": "Base Type", "type": "string"},
                    },
                    "required": ["base_type"],
                },
            }
        },
    }
