from typing import Any, Callable, Optional, Union, List

from apispec import APISpec
from chalice import Blueprint
from chalice.app import Chalice
from pydantic import BaseModel

from chalice_spec import Docs, Operation


def default_docs_for_methods(methods: List[str]):
    """
    Generate default documentation if desired.

    Originally contributed by Hamish Fagg
    """
    return Docs(
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


class BlueprintWithSpec(Blueprint):
    """
    A Chalice Blueprint that has been augmented with chalice-spec to
    enable easy OpenAPI documentation.
    """

    def __init__(self, import_name: str) -> None:
        self._chalice_spec_docs = []
        super(BlueprintWithSpec, self).__init__(import_name)

    def route(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        docs: Docs = kwargs.pop("docs", None)

        if docs:
            methods = [method.lower() for method in kwargs.get("methods", ["get"])]
            self._chalice_spec_docs.append((path, methods, docs))

        return super(BlueprintWithSpec, self).route(path, **kwargs)


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

    def __init__(self, app_name: str, spec: APISpec, generate_default_docs=False):
        super().__init__(app_name)

        self.__spec = spec
        self.__generate_default_docs = generate_default_docs

    def register_blueprint(
        self,
        blueprint: Union[Blueprint, BlueprintWithSpec],
        name_prefix: Optional[str] = None,
        url_prefix: Optional[str] = None,
    ) -> None:
        if isinstance(blueprint, BlueprintWithSpec):
            for path, methods, docs in blueprint._chalice_spec_docs:
                path = (url_prefix if url_prefix else "") + path

                if docs is None and self.__generate_default_docs:
                    docs = default_docs_for_methods(methods)

                if docs:
                    operations = docs.build_operations(self.__spec, methods)
                    self.__spec.path(path, operations=operations, summary=docs.summary)

        return super(ChaliceWithSpec, self).register_blueprint(
            blueprint, name_prefix=name_prefix, url_prefix=url_prefix
        )

    def route(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        docs: Docs = kwargs.pop("docs", None)
        methods = [method.lower() for method in kwargs.get("methods", ["get"])]

        if docs is None and self.__generate_default_docs:
            docs = default_docs_for_methods(methods)

        if docs:
            operations = docs.build_operations(self.__spec, methods)
            self.__spec.path(path, operations=operations, summary=docs.summary)

        return super(ChaliceWithSpec, self).route(path, **kwargs)
