from typing import Any, Union

from apispec import BasePlugin
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
        model: Union[BaseModel, None] = kwargs.pop("model")
        if model:
            schema = model.schema(ref_template="#/components/schemas/{model}")

            # Pydantic doesn't know that we are aggregating all of our models separately,
            # so we need to delete its attempts at being smart.
            if "definitions" in schema:
                del schema["definitions"]

            return schema

        return None
