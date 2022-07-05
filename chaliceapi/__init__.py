from apispec import APISpec, BasePlugin
from pydantic import BaseModel
from typing import Union, Any


class PydanticPlugin(BasePlugin):
    """
    An APISpec plugin that will register Pydantic models with APISpec.

    Uses the built-in schema export provided by Pydantic with minor modifications to provide
    the right structure for OpenAPI.

    Example:
        from pydantic import BaseModel

        class MyModel(BaseModel):
            hello: str
            world: str

        spec = APISPec(plugins=[PydanticPlugin()])
        spec.components.schema("MyModel", model=MyModel)
    """

    def schema_helper(
        self, name: str, definition: dict, **kwargs: Any
    ) -> Union[dict, None]:
        model: Union[BaseModel, None] = kwargs.pop("model")
        if model:
            schema = model.schema(ref_template="#/components/schemas/{model}")

            # Pydantic doesn't know that we are aggregating all of our models separately,
            # so we need to delete its attempts at being smart.
            if "definitions" in schema:
                del schema["definitions"]

            return schema

        return None


class ChalicePlugin(BasePlugin):
    """
    An APISpec plugin which will monkeypatch Chalice in order to allow for very
    convenient API documentation. It is designed to work with in conjunction with
    the PydanticPlugin.

    For example...

    @app.route('/hello',
               post_body_model=APydanticModel,
               post_response_body=APydanticModel)
    def hello():
        return {"world": "The quick brown fox jumps over the lazy dog."}
    """

    def __init__(self, auto_register_models=True):
        self.auto_register_models = auto_register_models

    def _handle_request(self, spec, method, kwargs):
        # First, look for a request body
        model_name = f"{method}_body_model"
        model = kwargs.pop(model_name, None)
        if not model:
            return {}

        # Register the model
        if self.auto_register_models:
            spec.components.schema(model.__name__, model=model)

        operations = {
            method: {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": model.__name__,
                        }
                    }
                }
            }
        }

        return operations

    def _handle_response(self, spec, method, kwargs):
        # Now the response!
        model_name = f"{method}_response_body"
        model = kwargs.pop(model_name, None)
        if not model:
            return {}

        if self.auto_register_models:
            spec.components.schema(model.__name__, model=model)

        description = kwargs.pop(
            f"{method}_response_description", "Successful response"
        )
        code = kwargs.pop(f"{method}_response_code", "200")

        operations = {
            method: {
                "responses": {
                    code: {
                        "description": description,
                        "content": {
                            "application/json": {
                                "schema": model.__name__,
                            }
                        },
                    }
                }
            }
        }

        return operations

    def init_spec(self, spec: APISpec) -> None:
        """
        When we initialize the spec, we should also monkeypatch the Chalice app
        we are working with.

        :param spec: APISpec object to work with
        :return: None
        """
        chalice_app = spec.options.pop("chalice_app")

        original_route = chalice_app.route

        def route(path, **kwargs):
            """
            Register a new route on a Chalice app. Monekypatched to support APISpec instructions.
            :param path: The path to use.
            :param kwargs: Additional Chalice kwargs and APIspec definitions.
            """
            methods = kwargs.get("methods", ["GET"])
            methods = list(map(str.lower, methods))

            operations = {}
            for method in methods:
                operations = {
                    **operations,
                    **self._handle_request(spec, method, kwargs),
                }
                operations = {
                    **operations,
                    **self._handle_response(spec, method, kwargs),
                }

            return_value = original_route(path, **kwargs)
            spec.path(path, operations=operations)
            return return_value

        chalice_app.route = route
