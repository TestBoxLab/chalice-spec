from typing import Any, Union

from apispec import BasePlugin, APISpec
from apispec.exceptions import DuplicateComponentNameError
from pydantic import BaseModel


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
        model: Union[BaseModel, None] = kwargs.pop("model", None)
        if model:
            schema = model.schema(ref_template="#/components/schemas/{model}")

            # If the spec has passed, we probably have nested models to contend with.
            spec: Union[APISpec, None] = kwargs.pop("spec", None)
            if spec and "definitions" in schema:
                for (k, v) in schema["definitions"].items():
                    try:
                        spec.components.schema(k, v)
                    except DuplicateComponentNameError:
                        pass

            if "definitions" in schema:
                del schema["definitions"]

            return schema

        return None
