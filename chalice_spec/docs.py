from typing import Type, Optional, Union, List

from apispec import APISpec
from pydantic import BaseModel

DEFAULT_DESCRIPTION = "Success"
DEFAULT_CODE = 200


class Response:
    def __init__(self, model: type, code: int = 200, description: str = "Success"):
        self.model = model
        self.code = code
        self.description = description


class Operation:
    def __init__(
        self,
        request: Optional[Type[BaseModel]] = None,
        response: Optional[Union[Response, Type[BaseModel]]] = None,
        responses: Optional[List[Response]] = None,
    ):
        self.request = request

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
        request: Type[BaseModel] = None,
        response: Union[Response, Type[BaseModel]] = None,
        responses: List[Response] = None,
    ):
        self.summary = summary

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
    def _build_operation_from_operation(cls, method: Operation, spec: APISpec):
        operation = {}

        if method.request:
            if method.request.__name__ not in spec.components.schemas:
                spec.components.schema(
                    method.request.__name__, model=method.request, spec=spec
                )
            operation["requestBody"] = {
                "content": {
                    "application/json": {
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

        return operation

    @classmethod
    def _build_operation_from_model(cls, model: Type[BaseModel], spec: APISpec):
        return cls._build_operation_from_operation(Operation(response=model), spec)

    @classmethod
    def _build_operation(cls, method: Method, spec: APISpec):
        if isinstance(method, Operation):
            return cls._build_operation_from_operation(method, spec)
        else:
            return cls._build_operation_from_model(method, spec)

    def _build_simple_operation(self, spec: APISpec):
        return self._build_operation_from_operation(
            Operation(
                request=self.request, response=self.response, responses=self.responses
            ),
            spec,
        )

    def build_operations(self, spec: APISpec, methods: List[str]):
        operations = {}

        if self.request or self.responses or self.response:
            if len(methods) != 1:
                raise TypeError(
                    "You can only use Docs short-hand for single-method API routes."
                )

            operations[methods[0].lower()] = self._build_simple_operation(spec)

        else:
            for method in self.methods:
                if getattr(self, method):
                    operations[method] = self._build_operation(
                        getattr(self, method), spec
                    )

        return operations


Resp = Response
Op = Operation
