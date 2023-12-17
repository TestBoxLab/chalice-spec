from chalice_spec.runtime.models.bedrock_agent import (
    BedrockAgentEventModel,
    BedrockAgentResponseModel,
)


def is_bedrock_agent_event(event: dict) -> bool:
    """
    Check event is bedrock agent event.
    """
    try:
        BedrockAgentEventModel.parse_obj(event)
        return True
    except Exception:
        # throw pydantic -> event is not Bedrock Agent Event
        return False


def empty_bedrock_agent_event() -> BedrockAgentEventModel:
    """
    Create empty bedrock agent event.
    """
    return BedrockAgentEventModel.parse_obj(
        {
            "messageVersion": "1.0",
            "agent": {
                "name": "",
                "id": "",
                "alias": "",
                "version": "",
            },
            "inputText": "",
            "sessionId": "",
            "actionGroup": "",
            "apiPath": "",
            "httpMethod": "",
            "parameters": [],
            "requestBody": {"content": {}},
        }
    )


def empty_bedrock_agent_response() -> BedrockAgentResponseModel:
    """
    Create empty bedrock agent response.
    """
    return BedrockAgentResponseModel.parse_obj(
        {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": "",
                "apiPath": "",
                "httpMethod": "",
                "httpStatusCode": 0,
                "responseBody": {},
            },
        }
    )
