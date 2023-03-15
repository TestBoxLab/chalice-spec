import re
from apispec import BasePlugin, APISpec
from pydantic import BaseModel

from chalice_spec.docs import Docs, Operation, trim_docstring


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

    def __init__(self, generate_default_docs: bool = False):
        super(ChalicePlugin, self).__init__()
        self._generate_default_docs = generate_default_docs

    def init_spec(self, spec: APISpec) -> None:
        """
        When we initialize the spec, we should also monkeypatch the Chalice app
        we are working with.

        :param spec: APISpec object to work with
        :return: None
        """
        chalice_app = spec.options.pop("chalice_app")

        original_route = chalice_app.route

        def route(path: str, **kwargs):
            """
            Register a new route on a Chalice app. Monekypatched to support APISpec instructions.
            :param path: The path to use.
            :param methods: the allowable methods and their documentation
            :param kwargs: Additional Chalice kwargs and APIspec definitions.
            """

            def route_decorator(func):
                docs: Docs = kwargs.pop("docs", None)
                methods = [method.lower() for method in kwargs.get("methods", ["get"])]

                if docs is None and self._generate_default_docs:
                    docs = Docs(
                        **{
                            method: Operation(
                                response=BaseModel,
                                request=(
                                    None
                                    if method in ["get", "delete", "head", "options"]
                                    else BaseModel
                                ),
                            )
                            for method in methods
                        }
                    )

                if docs:
                    operations = docs.build_operations(spec, methods)

                    # Infer path parameters
                    get_params = r"{([^}]+)}"
                    path_params = []
                    for param in re.findall(get_params, path):
                        path_params.append(
                            {
                                "in": "path",
                                "name": param,
                                "schema": {"type": "string"},
                                "required": True,
                            }
                        )

                    # Infer tags
                    for operation in operations:
                        if (
                            "tags" not in operations[operation]
                            or not operations[operation]["tags"]
                        ):
                            operations[operation]["tags"] = [
                                "/" + path.lstrip("/").split("/", 1)[0]
                            ]

                    # Infer summary and description from route docstrings
                    if func.__doc__:
                        split_docstring = trim_docstring(func.__doc__).split("\n", 1)
                        for operation in operations:
                            if (
                                "summary" not in operations[operation]
                                or not operations[operation]["summary"]
                            ):
                                operations[operation]["summary"] = split_docstring[0]
                            if (
                                "description" not in operations[operation]
                                or not operations[operation]["description"]
                            ) and len(split_docstring) == 2:
                                operations[operation]["description"] = split_docstring[
                                    1
                                ].strip()

                    spec.path(
                        path,
                        operations=operations,
                        summary=docs.summary,
                        parameters=path_params,
                    )
                return original_route(path, **kwargs)(func)

            return route_decorator

        chalice_app.route = route
