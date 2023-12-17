from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, root_validator, Field


class ApiGatewayUserCertValidity(BaseModel):
    notBefore: str
    notAfter: str


class ApiGatewayUserCert(BaseModel):
    clientCertPem: str
    subjectDN: str
    issuerDN: str
    serialNumber: str
    validity: ApiGatewayUserCertValidity


class APIGatewayEventIdentity(BaseModel):
    accessKey: Optional[str] = None
    accountId: Optional[str] = None
    apiKey: Optional[str] = None
    apiKeyId: Optional[str] = None
    caller: Optional[str] = None
    cognitoAuthenticationProvider: Optional[str] = None
    cognitoAuthenticationType: Optional[str] = None
    cognitoIdentityId: Optional[str] = None
    cognitoIdentityPoolId: Optional[str] = None
    principalOrgId: Optional[str] = None
    sourceIp: str
    user: Optional[str] = None
    userAgent: Optional[str] = None
    userArn: Optional[str] = None
    clientCert: Optional[ApiGatewayUserCert] = None


class APIGatewayEventAuthorizer(BaseModel):
    claims: Optional[Dict[str, Any]] = None
    scopes: Optional[List[str]] = None


class APIGatewayEventRequestContext(BaseModel):
    accountId: Optional[str] = None
    apiId: Optional[str] = None
    authorizer: Optional[APIGatewayEventAuthorizer] = None
    stage: Optional[str] = None
    protocol: Optional[str] = None
    identity: APIGatewayEventIdentity
    requestId: Optional[str] = None
    requestTime: Optional[str] = None
    requestTimeEpoch: datetime = Field(datetime.utcnow())
    resourceId: Optional[str] = None
    resourcePath: str
    domainName: Optional[str] = None
    domainPrefix: Optional[str] = None
    extendedRequestId: Optional[str] = None
    httpMethod: str
    path: str
    connectedAt: Optional[datetime] = None
    connectionId: Optional[str] = None
    eventType: Optional[str] = None
    messageDirection: Optional[str] = None
    messageId: Optional[str] = None
    routeKey: Optional[str] = None
    operationName: Optional[str] = None

    @root_validator(allow_reuse=True, skip_on_failure=True)
    def check_message_id(cls, values):
        message_id, event_type = values.get("messageId"), values.get("eventType")
        if message_id is not None and event_type != "MESSAGE":
            raise ValueError(
                "messageId is available only when the `eventType` is `MESSAGE`"
            )
        return values


class APIGatewayProxyEventModel(BaseModel):
    version: Optional[str] = None
    resource: Optional[str] = None
    path: Optional[str] = None
    httpMethod: str = Field("")
    headers: Dict[str, str]
    multiValueHeaders: Dict[str, List[str]] = Field({})
    queryStringParameters: Optional[Dict[str, str]] = None
    multiValueQueryStringParameters: Optional[Dict[str, List[str]]] = None
    requestContext: APIGatewayEventRequestContext
    pathParameters: Optional[Dict[str, str]] = None
    stageVariables: Optional[Dict[str, str]] = None
    isBase64Encoded: bool = Field(False)
    body: Optional[Union[str, Type[BaseModel]]] = None
