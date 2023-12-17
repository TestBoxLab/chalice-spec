from chalice.app import Chalice
from chalice_spec.runtime.converter.bedrock_agent_event_to_apigw import (
    BedrockAgentEventToApiGateway,
)
from enum import Enum
from typing import List, Optional

from chalice_spec.runtime.model_utility.apigw import is_api_gateway_event
from chalice_spec.runtime.model_utility.bedrock_agent import is_bedrock_agent_event


class APIRuntime(Enum):
    """
    Constants: Run on Chalice
    """

    APIGateway = "api-gateway"
    BedrockAgent = "bedrock-agent"


"""
Runtime Constants
"""

# Allow to call from API Gateway or run local
APIRuntimeApiGateway = [APIRuntime.APIGateway]
# Allow to call from Bedrock Agent
APIRuntimeBedrockAgent = [APIRuntime.BedrockAgent]
# Allow to call from API Gateway or Bedrock Agent or run local
APIRuntimeAll = [APIRuntime.APIGateway, APIRuntime.BedrockAgent]


class APIRuntimeHandler:
    """
    Mixin : add __call__ method
    """

    _runtime: Optional[List[APIRuntime]] = None

    def set_runtime_handler(self, runtime: List[APIRuntime]):
        """
        Set Runtime Handler
        Default is invoke by API Gateway
        """
        self._runtime = runtime

    def __call__(self, event: dict, context: dict):
        """
        This method will be called by lambda event handler.
        event is lambda event, context is lambda context.
        """
        # Not set runtime
        if self._runtime is None:
            # Default Runtime
            return Chalice.__call__(self, event, context)

        converter = None
        # Called by Bedrock Agent
        if (APIRuntime.BedrockAgent in self._runtime) and is_bedrock_agent_event(event):
            converter = BedrockAgentEventToApiGateway()

        # Called by API Gateway
        if (APIRuntime.APIGateway in self._runtime) and is_api_gateway_event(event):
            return Chalice.__call__(self, event, context)

        # Unknown, or default caller
        if converter is None:
            # Not found converter
            raise Exception("Not found converter")

        # Invoke parent __call__ method
        api_gateway_response = Chalice.__call__(
            self, event=converter.convert_request(event), context=context
        )
        # Return lambda result
        return converter.convert_response(event, api_gateway_response)
