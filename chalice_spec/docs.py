import sys
from typing import Type, Optional, Union, List, Dict

from apispec import APISpec
from pydantic import BaseModel

DEFAULT_DESCRIPTION = "Success"
DEFAULT_CODE = 200


class Response:
    """
    A response that your API might provide. Provide the Pydantic model,
    plus the HTTP status code that would be returned with this model,
    and an optional description.
    """

    def __init__(self, model: type, code: int = 200, description: str = "Success"):
        self.model = model
        self.code = code
        self.description = description


class Operation:
    """
    Represents a single Operation, as defined by OpenAPI, which is generally
    a request, plus a set of responses.
    """

    def __init__(
        self,
        summary: str = None,
        description: str = None,
        tags: List[str] = None,
        parameters: List[Dict] = None,
        content_types: List[str] = None,
        request: Optional[Type[BaseModel]] = None,
        response: Optional[Union[Response, Type[BaseModel]]] = None,
        responses: Optional[List[Response]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
    ):
        self.summary = summary
        self.description = description
        self.tags = tags
        self.parameters = parameters

        self.content_types = content_types
        self.request = request
        self.security = security

        if response and responses:
            raise TypeError("You must only pass one of response or responses")

        if response:
            self._populate_response(response)
        else:
            self._populate_responses(responses)

    def _populate_response(self, response: Union[Response, type]):
        if isinstance(response, Response):
            # If this is a Response object, we can track it as-is.
            self.responses = {response.code: response}
        else:
            # If not, we will use sensible defaults
            self.responses = {DEFAULT_CODE: Response(model=response)}

    def _populate_responses(self, responses: List[Response]):
        self.responses = {}
        for response in responses:
            if response.code in self.responses:
                raise TypeError(
                    "You  must only specify one response per HTTP status code"
                )
            self.responses[response.code] = response


Method = Union[Type[BaseModel], Operation]


class Docs:
    """
    Chalice-Spec documentation for an API endpoint that will eventually
    result in an OpenAPI spec!
    """

    methods = ["get", "post", "put", "patch", "delete", "head", "options"]

    def __init__(
        self,
        summary: str = None,
        get: Method = None,
        post: Method = None,
        put: Method = None,
        patch: Method = None,
        delete: Method = None,
        head: Method = None,
        options: Method = None,
        content_types: List[str] = None,
        request: Type[BaseModel] = None,
        response: Union[Response, Type[BaseModel]] = None,
        responses: List[Response] = None,
    ):
        self.summary = summary

        self.content_types = content_types
        self.request = request
        self.response = response
        self.responses = responses

        self.get = get
        self.post = post
        self.put = put
        self.patch = patch
        self.delete = delete
        self.head = head
        self.options = options

        # check to make sure we haven't violated the contract
        if self.request or self.response or self.responses:
            for method in self.methods:
                if getattr(self, method):
                    raise TypeError(
                        "You must choose either a short-hand or long-hand Docs, not both."
                    )

    @classmethod
    def _build_operation_from_operation(
        cls, method: Operation, spec: APISpec, content_types: List[str] = None
    ):
        operation = {}

        if method.request:
            if method.request.__name__ not in spec.components.schemas:
                spec.components.schema(
                    method.request.__name__, model=method.request, spec=spec
                )
            content_type = (
                method.content_types[0]
                if method.content_types
                else content_types[0]
                if content_types
                else "application/json"
            )
            operation["requestBody"] = {
                "content": {
                    content_type: {
                        "schema": method.request.__name__,
                    }
                }
            }

        if method.responses:
            responses = {}

            for code, response in method.responses.items():
                if response.model.__name__ not in spec.components.schemas:
                    spec.components.schema(
                        response.model.__name__,
                        model=response.model,
                        spec=spec,
                    )
                responses[code] = {
                    "description": response.description,
                    "content": {
                        "application/json": {
                            "schema": response.model.__name__,
                        }
                    },
                }

            operation["responses"] = responses

        if method.summary:
            operation["summary"] = method.summary
        if method.description:
            operation["description"] = method.description
        if method.tags:
            operation["tags"] = method.tags
        if method.parameters:
            operation["parameters"] = method.parameters
        if method.security:
            operation["security"] = method.security

        return operation

    @classmethod
    def _build_operation_from_model(
        cls, model: Type[BaseModel], spec: APISpec, content_types: List[str] = None
    ):
        return cls._build_operation_from_operation(
            Operation(content_types=content_types, response=model), spec
        )

    @classmethod
    def _build_operation(
        cls, method: Method, spec: APISpec, content_types: List[str] = None
    ):
        if isinstance(method, Operation):
            return cls._build_operation_from_operation(method, spec, content_types)
        else:
            return cls._build_operation_from_model(method, spec, content_types)

    def _build_simple_operation(self, spec: APISpec, content_types: List[str] = None):
        return self._build_operation_from_operation(
            Operation(
                content_types=content_types,
                request=self.request,
                response=self.response,
                responses=self.responses,
            ),
            spec,
        )

    def build_operations(
        self, spec: APISpec, methods: List[str], content_types: List[str] = None
    ):
        operations = {}

        if self.request or self.responses or self.response:
            if len(methods) != 1:
                raise TypeError(
                    "You can only use Docs short-hand for single-method API routes."
                )

            operations[methods[0].lower()] = self._build_simple_operation(
                spec, content_types
            )

        else:
            for method in self.methods:
                if getattr(self, method):
                    operations[method] = self._build_operation(
                        getattr(self, method), spec, content_types
                    )

        return operations


Resp = Response
Op = Operation


# From: https://peps.python.org/pep-0257/#handling-docstring-indentation
def trim_docstring(docstring):
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return "\n".join(trimmed)
