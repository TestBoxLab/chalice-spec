import re

from chalice_spec.docs import trim_docstring
from chalice_spec import Docs, Operation
from typing import Any, Callable, Optional, Union, List

from apispec import APISpec
from chalice import Blueprint
from chalice.app import Chalice
from pydantic import BaseModel


def default_docs_for_methods(
    methods: List[str], content_types: Optional[List[str]] = None
):
    """
    Generate default documentation if desired.

    Originally contributed by Hamish Fagg
    """
    return Docs(
        **{
            method: Operation(
                content_types=content_types,
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


class BlueprintWithSpec(Blueprint):
    """
    A Chalice Blueprint that has been augmented with chalice-spec to
    enable easy OpenAPI documentation.
    """

    def __init__(self, import_name: str, tags=None) -> None:
        self._chalice_spec_docs = []
        self._chalice_spec_tags = tags
        super(BlueprintWithSpec, self).__init__(import_name)

    def route(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        def route_decorator(func):
            docs: Docs = kwargs.pop("docs", None)

            methods = [method.lower() for method in kwargs.get("methods", ["get"])]
            content_types = kwargs.get("content_types", ["application/json"])

            self._chalice_spec_docs.append((path, methods, content_types, docs, func))

            return super(BlueprintWithSpec, self).route(path, **kwargs)(func)

        return route_decorator


class ChaliceWithSpec(Chalice):
    """
    A Chalice app that has been augmented with chalice-spec to enable
    easy OpenAPI documentation.

    Here is a simple example that makes some assumptions...

    from chalice_spec import ChaliceWithSpec, Docs, Op

    app = ChaliceWithSpec(spec=an_api_spec_previously_defined)

    @app.route('/hello',
               docs=APydanticModel)
    def hello():
        return {"world": "The quick brown fox jumps over the lazy dog."}

    However, you will more likely want to utilize the full Docs object.

    @app.route("/world", docs=Docs(get=APydanticModel,
                                   post=Op(request=MyRequestModel,
                                           response=MyResponseModel)))
    def world():
        if app.current_request.method == "get":
            return {"an object": "that matches", "the schema": "APydantcModel"}
        # and so on!
    """

    def __init__(
        self, app_name: str, spec: APISpec, generate_default_docs=False, **kwargs
    ):
        super().__init__(app_name, **kwargs)

        self.__spec = spec
        self.__generate_default_docs = generate_default_docs

    def decorate(self, docs, path, methods, content_types, func, tags) -> None:
        if docs is None and self.__generate_default_docs:
            docs = default_docs_for_methods(methods, content_types)

        if docs:
            operations = docs.build_operations(self.__spec, methods, content_types)

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
                    or operations[operation]["tags"] is None
                ):
                    if tags:
                        operations[operation]["tags"] = tags
                    else:
                        operations[operation]["tags"] = [
                            "/" + path.lstrip("/").split("/", 1)[0]
                        ]

            # Infer summary and description from route docstrings
            if func.__doc__:
                split_docstring = trim_docstring(func.__doc__).split("\n", 1)
                for operation in operations:
                    if (
                        "summary" not in operations[operation]
                        or operations[operation]["summary"] is None
                    ):
                        operations[operation]["summary"] = split_docstring[0]
                    if (
                        "description" not in operations[operation]
                        or operations[operation]["description"] is None
                    ) and len(split_docstring) == 2:
                        operations[operation]["description"] = split_docstring[
                            1
                        ].strip()

            self.__spec.path(
                path,
                operations=operations,
                summary=docs.summary,
                parameters=path_params,
            )

    def register_blueprint(
        self,
        blueprint: Union[Blueprint, BlueprintWithSpec],
        name_prefix: Optional[str] = None,
        url_prefix: Optional[str] = None,
    ) -> None:
        if isinstance(blueprint, BlueprintWithSpec):
            for (
                path,
                methods,
                content_types,
                docs,
                func,
            ) in blueprint._chalice_spec_docs:
                path = (url_prefix if url_prefix else "") + path

                self.decorate(
                    docs,
                    path,
                    methods,
                    content_types,
                    func,
                    blueprint._chalice_spec_tags,
                )

        return super(ChaliceWithSpec, self).register_blueprint(
            blueprint, name_prefix=name_prefix, url_prefix=url_prefix
        )

    def route(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        def route_decorator(func):
            docs: Docs = kwargs.pop("docs", None)
            methods = [method.lower() for method in kwargs.get("methods", ["get"])]
            content_types = kwargs.get("content_types", None)

            self.decorate(docs, path, methods, content_types, func, None)

            return super(ChaliceWithSpec, self).route(path, **kwargs)(func)

        return route_decorator
