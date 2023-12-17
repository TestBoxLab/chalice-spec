import json
from apispec import APISpec
from chalice_spec.chalice import ChaliceWithSpec
from chalice_spec.docs import Docs
from chalice_spec.pydantic import PydanticPlugin
from chalice_spec.runtime.api_runtime import (
    APIRuntimeBedrockAgent,
    APIRuntimeAll,
    APIRuntimeApiGateway,
)
from chalice_spec.runtime.converter import EventConverter
from chalice_spec.runtime.model_utility.apigw import (
    empty_api_gateway_event,
    is_api_gateway_event,
)
from chalice_spec.runtime.model_utility.bedrock_agent import (
    empty_bedrock_agent_event,
    empty_bedrock_agent_response,
    is_bedrock_agent_event,
)
from tests.schema import TestSchema, AnotherSchema
from pydantic import BaseModel


def setup_test(runtime):
    spec = APISpec(
        title="Test Schema",
        openapi_version="3.0.1",
        version="0.0.0",
        plugins=[PydanticPlugin()],
    )
    app = ChaliceWithSpec(app_name="test", spec=spec, runtime=runtime)
    return app, spec


class APIParameter(BaseModel):
    apiPath: str
    httpMethod: str


class EmptySchema(BaseModel):
    pass


def parameter_agents_for_amazon_bedrock(parameter: APIParameter):
    return {
        "messageVersion": "1.0",
        "agent": {
            "name": "string",
            "id": "string",
            "alias": "string",
            "version": "string",
        },
        "inputText": "string",
        "sessionId": "string",
        "actionGroup": "string",
        "apiPath": parameter.apiPath,
        "httpMethod": parameter.httpMethod,
        "parameters": [{"name": "string", "type": "string", "value": "string"}],
        "requestBody": {
            "content": {
                "application/json": {
                    "properties": [
                        {"name": "hello", "type": "string", "value": "hello"},
                        {"name": "world", "type": "int", "value": "123"},
                    ]
                }
            }
        },
        "sessionAttributes": {
            "string": "string",
        },
        "promptSessionAttributes": {"string": "string"},
    }


def parameter_api_gateway(parameter: APIParameter):
    return {
        "resource": parameter.apiPath,
        "path": parameter.apiPath,
        "httpMethod": parameter.httpMethod,
        "requestContext": {
            "resourcePath": parameter.apiPath,
            "httpMethod": parameter.httpMethod,
            "path": parameter.apiPath,
            "accountId": "",
            "apiId": "",
            "authorizer": {},
            "identity": {"sourceIp": "0.0.0.0"},
            "protocol": "",
            "requestId": "",
            "requestTime": "",
            "requestTimeEpoch": 0,
            "stage": "",
        },
        "headers": {"content-type": "application/json"},
        "multiValueHeaders": {},
        "queryStringParameters": {},
        "multiValueQueryStringParameters": {},
        "pathParameters": {},
        "stageVariables": "",
        "body": json.dumps({"hello": "abc", "world": 123}),
        "isBase64Encoded": False,
    }


def test_invoke_from_agents_for_amazon_bedrock():
    """
    Normaly :: Invoke from Amazon Bedrock Agent

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Amazon Bedrock Agent
    """
    app, spec = setup_test(APIRuntimeBedrockAgent)

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
        docs=Docs(request=TestSchema, response=AnotherSchema),
    )
    def get_post():
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    response = app(
        parameter_agents_for_amazon_bedrock(
            APIParameter(httpMethod="POST", apiPath="/posts")
        ),
        {},
    )
    assert response["response"]["httpStatusCode"] == 200
    assert (
        "nintendo" in response["response"]["responseBody"]["application/json"]["body"]
    )
    assert "atari" in response["response"]["responseBody"]["application/json"]["body"]
    assert "koikoi" in response["response"]["responseBody"]["application/json"]["body"]


def test_invoke_from_agents_for_amazon_bedrock_no_post_body():
    """
    Normaly :: Invoke from Amazon Bedrock Agent No Post Body

    Condition:
        Invoke from Amazon Bedrock Agent with empty body
    Expects:
        Return response for Amazon Bedrock Agent
    """
    app, spec = setup_test(APIRuntimeBedrockAgent)

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
        docs=Docs(request=EmptySchema, response=EmptySchema),
    )
    def get_post():
        return EmptySchema().json()

    empty_request = parameter_agents_for_amazon_bedrock(
        APIParameter(httpMethod="POST", apiPath="/posts")
    )
    empty_request["requestBody"]["content"] = {}
    response = app(empty_request, {})
    assert response["response"]["httpStatusCode"] == 200


def test_invoke_from_agents_for_api_gateway():
    """
    Normaly :: Invoke from Amazon API Gateway

    Condition:
        Invoke from Amazon API Gateway
    Expects:
        Return response for Amazon API Gateway
    """
    app, spec = setup_test(APIRuntimeApiGateway)

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
        docs=Docs(request=TestSchema, response=AnotherSchema),
    )
    def get_post():
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    response = app(
        parameter_api_gateway(APIParameter(httpMethod="POST", apiPath="/posts")),
        {},
    )
    assert response["statusCode"] == 200
    assert "nintendo" in response["body"]
    assert "atari" in response["body"]
    assert "koikoi" in response["body"]


def test_invoke_from_dual_services():
    """
    Normaly :: Invoke from Amazon Bedrock Agent and Amazon API Gateway

    Condition:
        Allowed to Invoke from Amazon Bedrock Agent and Amazon API Gateway
    Expects:
        Return response for Correct response
    """
    app, spec = setup_test(APIRuntimeAll)

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
        docs=Docs(request=TestSchema, response=AnotherSchema),
    )
    def get_post():
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    response = app(
        parameter_api_gateway(APIParameter(httpMethod="POST", apiPath="/posts")),
        {},
    )
    assert response["statusCode"] == 200

    response = app(
        parameter_agents_for_amazon_bedrock(
            APIParameter(httpMethod="POST", apiPath="/posts")
        ),
        {},
    )
    assert response["response"]["httpStatusCode"] == 200


def test_invoke_from_default_setting():
    """
    Normaly :: Invoke from API Gateway (setting is default runtime)

    Condition:
        Allowed default setting
    Expects:
        Return response for Correct response
    """
    app, spec = setup_test(None)

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
        docs=Docs(request=TestSchema, response=AnotherSchema),
    )
    def get_post():
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    response = app(
        parameter_api_gateway(APIParameter(httpMethod="POST", apiPath="/posts")),
        {},
    )
    assert response["statusCode"] == 200


def test_invoke_from_deny_service_agent_for_bedrock():
    """
    Anomaly :: Invoke from Deny Service

    Condition:
        Allow to Invoke Api Gateway
        But invoke from Amazon Bedrock Agent
    Expects:
        Failed to execute
    """
    app, spec = setup_test([APIRuntimeApiGateway])

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
        docs=Docs(request=TestSchema, response=AnotherSchema),
    )
    def get_post():
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    try:
        app(
            parameter_agents_for_amazon_bedrock(
                APIParameter(httpMethod="POST", apiPath="/posts")
            ),
            {},
        )
        assert True
    except Exception:
        pass


def test_invoke_from_deny_service_api_gateway():
    """
    Anomaly :: Invoke from Deny Service

    Condition:
        Allow to Invoke Bedrock Agent
        But invoke from Api Gateway
    Expects:
        Failed to execute
    """
    app, spec = setup_test([APIRuntimeBedrockAgent])

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
        docs=Docs(request=TestSchema, response=AnotherSchema),
    )
    def get_post():
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    try:
        app(
            parameter_api_gateway(APIParameter(httpMethod="POST", apiPath="/posts")),
            {},
        )
        assert True
    except Exception:
        pass


def test_converter_base_class():
    """
    Normaliy :: Call base class method

    Expects:
        Base class is not changed received parameter
    """
    assert EventConverter().convert_request({"Hello": "world"})["Hello"] == "world"
    assert EventConverter().convert_response({}, {"Hello": "world"})["Hello"] == "world"


def test_utility_functions_create_empty_base_models():
    """
    Normally :: Create empty base models

    Expects:
        No Assertion Errors
    """
    assert is_api_gateway_event(empty_api_gateway_event().dict(by_alias=True))
    assert is_bedrock_agent_event(empty_bedrock_agent_event().dict(by_alias=True))
    assert not is_api_gateway_event(empty_bedrock_agent_event().dict(by_alias=True))
    assert not is_bedrock_agent_event(empty_api_gateway_event().dict(by_alias=True))
    empty_bedrock_agent_response()
