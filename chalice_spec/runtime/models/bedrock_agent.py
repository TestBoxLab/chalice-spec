from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class BedrockAgentModel(BaseModel):
    name: str
    id_: str = Field(..., alias="id")
    alias: str
    version: str


class BedrockAgentPropertyModel(BaseModel):
    name: str
    type_: str = Field(..., alias="type")
    value: str


class BedrockAgentRequestMediaModel(BaseModel):
    properties: List[BedrockAgentPropertyModel]


class BedrockAgentRequestBodyModel(BaseModel):
    content: Dict[str, BedrockAgentRequestMediaModel]


class BedrockAgentEventModel(BaseModel):
    # The version of the message that identifies the format of the event data going
    # into the Lambda function and the expected format of the response from a Lambda function.
    # Amazon Bedrock only supports version 1.0.
    message_version: str = Field(..., alias="messageVersion")
    # The user input for the conversation turn.
    input_text: str = Field(..., alias="inputText")
    # session_id – The unique identifier of the agent session.
    session_id: str = Field(..., alias="sessionId")
    # action_group – The name of the action group.
    action_group: str = Field(..., alias="actionGroup")
    # api_path – The path to the API operation, as defined in the OpenAPI schema.
    api_path: str = Field(..., alias="apiPath")
    # http_method – The method of the API operation, as defined in the OpenAPI schema.
    http_method: str = Field(..., alias="httpMethod")
    # session_attributes – Contains session attributes and their values.
    session_attributes: Dict[str, str] = Field({}, alias="sessionAttributes")
    # prompt_session_attributes – Contains prompt attributes and their values.
    prompt_session_attributes: Dict[str, str] = Field(
        {}, alias="promptSessionAttributes"
    )
    # Contains information about the name, ID, alias, and version of the agent that the action group belongs to.
    agent: BedrockAgentModel
    # parameters – Contains a list of objects. Each object contains the name, type,
    # and value of a parameter in the API operation, as defined in the OpenAPI schema.
    parameters: Optional[List[BedrockAgentPropertyModel]] = None
    # requestBody – Contains the request body and its properties, as defined in the OpenAPI schema.
    request_body: Optional[BedrockAgentRequestBodyModel] = Field(
        None, alias="requestBody"
    )


class BedrockAgentResponsePesponceBodyModel(BaseModel):
    """
    Bedrock Agent response parameter : nested response body
    """

    # Response body
    body: str


class BedrockAgentResponseParameterModel(BaseModel):
    """
    Bedrock Agent response data : nested parameter
    """

    # The name of the action group.
    action_group: str = Field(..., alias="actionGroup")
    # The path to the API operation, as defined in the OpenAPI schema.
    api_path: str = Field(..., alias="apiPath")
    # The method of the API operation, as defined in the OpenAPI schema.
    http_method: str = Field(..., alias="httpMethod")
    # Status Code
    http_status_code: int = Field(..., alias="httpStatusCode")
    # Contains the response body, as defined in the OpenAPI schema.
    response_body: Dict[str, BedrockAgentResponsePesponceBodyModel] = Field(
        ..., alias="responseBody"
    )
    # (Optional) sessionAttributes – Contains session attributes and their values.
    session_attributes: Optional[Dict[str, str]] = Field(
        None, alias="sessionAttributes"
    )
    # (Optional) promptSessionAttributes – Contains prompt attributes and their values.
    prompt_session_attributes: Optional[Dict[str, str]] = Field(
        None, alias="promptSessionAttributes"
    )

    def add_response_body(self, content_type: str, body: str) -> None:
        """
        Add response body
        """
        self.response_body[content_type] = BedrockAgentResponsePesponceBodyModel(
            body=body
        )


class BedrockAgentResponseModel(BaseModel):
    """
    Bedrock Agent response data
    """

    # The version of the message that identifies the format of the event data going
    # into the Lambda function and the expected format of the response from a Lambda function.
    # Amazon Bedrock only supports version 1.0.
    message_version: str = Field(..., alias="messageVersion")
    # Contains the following information about the API response.
    response: BedrockAgentResponseParameterModel
