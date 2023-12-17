import time
import boto3
import sys
from pydantic import BaseModel, Field
from pathlib import Path
import os
from hashlib import md5
from app import spec
import json
import io


class AgentsForAmazonBedrockConfig(BaseModel):
    """
    Amazon Bedrock Agent Config
    """

    # OpenAPI Schema File Name in S3 Bucket
    schema_file: str = Field("api-schema.json")
    # Bedrock Agent Instructions (Situsation settings for LLM)
    instructions: str = Field("You are AI agent.")
    # Bedrock Agent Version (Const: DRAFT)
    agent_version: str = Field("DRAFT")
    # Bedrock Agent Action Group Name
    agent_action_name: str = Field("Main")
    # Agent Service description
    description: str = Field("")
    # Session time
    idle_session_ttl_in_seconds: int = Field(900)
    # LLM Model ID
    foundation_model: str = Field("anthropic.claude-v2")


def read_agents_for_amazon_bedrock_config():
    """
    Read Config File
    """
    with open(str(Path(".chalice") / "agents-for-amazon-bedrock.json")) as fp:
        return AgentsForAmazonBedrockConfig.parse_raw(fp.read())


class ChaliceConfigFile(BaseModel):
    """
    Chalice Config File
    """

    # Chalice App Version
    version: str = Field("")
    # Chalice App Name
    app_name: str = Field("")


def read_config():
    """
    Read Config File
    """
    with open(str(Path(".chalice") / "config.json")) as fp:
        return ChaliceConfigFile.parse_raw(fp.read())


class CallerIdentity(BaseModel):
    UserId: str
    Account: str
    Arn: str
    Region: str = Field("us-east-1")
    ChaliceConfig: ChaliceConfigFile = Field(ChaliceConfigFile())
    AgentConfig: AgentsForAmazonBedrockConfig = Field(AgentsForAmazonBedrockConfig())
    Stage: str = Field("dev")

    @property
    def session(self):
        return boto3.Session(region_name=self.Region)

    @property
    def bucket_name(self):
        return f"agents-for-bedrock-{self.Account}-{self.project_hash}"

    @property
    def lambda_arn(self):
        return f"arn:aws:lambda:{self.Region}:{self.Account}:function:{self.ChaliceConfig.app_name}-{self.Stage}"

    @property
    def lambda_function_name(self):
        return f"{self.ChaliceConfig.app_name}-{self.Stage}"

    @property
    def agents_role_arn(self):
        return f"arn:aws:iam::{self.Account}:role/AmazonBedrockExecutionRoleForAgents_{self.project_hash}"

    @property
    def project_hash(self):
        return md5(self.ChaliceConfig.app_name.encode("utf-8")).hexdigest()[:8]

    @property
    def stack_name(self):
        return f"{self.ChaliceConfig.app_name}_stack".replace("_", "")

    def agent_id_to_arn(self, agent_id: str):
        return f"arn:aws:bedrock:{self.Region}:{self.Account}:agent/{agent_id}"


def read_identity():
    """
    Read Account Identity from STS
    """
    # Current Region (Read from current Environment variable)
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    # Create Session on Current Region
    session = boto3.Session(region_name=region)
    # Get Account Into
    identity = session.client("sts").get_caller_identity()
    # Parse with pydantic
    item = CallerIdentity.parse_obj(identity)
    # Set Current Region
    item.Region = region
    # Read config from .chalice/config.json
    item.ChaliceConfig = read_config()
    # Read config from .chalice/agents-for-amazon-bedrock.json
    item.AgentConfig = read_agents_for_amazon_bedrock_config()
    # Return Identity
    return item


class CurrentAgentInfo(BaseModel):
    """
    Agents for Amazon Bedrock Response Value
    """

    # Agent Id
    agent_id: str
    # Action Group Id
    action_group_id: str
    # Agent Status
    agent_status: str


def read_current_agent_info(
    identity: CallerIdentity, bedrock_agent
) -> CurrentAgentInfo:
    """
    Read Current Agent Info From AWS Cloud
    """
    # Get Agent Id
    agent_ids = [
        {
            "id": item["agentId"],  # Search Agent Id from Agent Name
            "status": item["agentStatus"],  # Search Agent Status from Agent Name
        }
        for item in bedrock_agent.list_agents()["agentSummaries"]
        if item["agentName"] == identity.ChaliceConfig.app_name
    ]
    if len(agent_ids) == 0:
        # No Agent id: Abort process
        print("not found agent")
        return None

    # Get Action Group Id
    action_group_ids = [
        item["actionGroupId"]  # Search Action Group Id from Action Group Name
        for item in bedrock_agent.list_agent_action_groups(
            agentId=agent_ids[0]["id"], agentVersion=identity.AgentConfig.agent_version
        )["actionGroupSummaries"]
        if item["actionGroupName"] == identity.AgentConfig.agent_action_name
    ]
    if len(action_group_ids) == 0:
        return CurrentAgentInfo(
            agent_id=agent_ids[0]["id"],
            agent_status=agent_ids[0]["status"],
            action_group_id="",
        )

    return CurrentAgentInfo(
        agent_id=agent_ids[0]["id"],
        agent_status=agent_ids[0]["status"],
        action_group_id=action_group_ids[0],
    )


def create_resource(identity: CallerIdentity, cfn):
    """
    Create Resource for Agent with CloudFormation
    """
    # Read Cloudformation template
    with open("template.yaml") as fp:
        template_body = fp.read()

    # Create Stack parameter
    # Required "Capability Named IAM"
    parameter = {
        "StackName": identity.stack_name,
        "TemplateBody": template_body,
        "Capabilities": ["CAPABILITY_NAMED_IAM"],
        "Parameters": [
            {"ParameterKey": "HashCode", "ParameterValue": identity.project_hash},
        ],
    }

    try:
        # Create Resources
        cfn.create_stack(**parameter)
    except Exception:
        # Update Resources
        cfn.update_stack(**parameter)


def init():
    """
    Command : init

    Create Initial Resource
    """
    # Read config
    identity = read_identity()

    # Create CloudFormation Client
    cfn = identity.session.client("cloudformation")

    print("Start : Init")

    # Create Cloudfomation Stack
    create_resource(identity, cfn)
    print(f"- Created stack : {identity.stack_name}")

    # Wait for complete
    waiter = cfn.get_waiter("stack_create_complete")
    waiter.wait(StackName=identity.stack_name)

    # Upload OpenAPI Schema File
    bucket = identity.session.resource("s3").Bucket(identity.bucket_name)
    with io.BytesIO(json.dumps(spec.to_dict()).encode("utf-8")) as fp:
        bucket.upload_fileobj(fp, identity.AgentConfig.schema_file)
    print(
        f"- Uploaded OpenAPI schema file to {identity.bucket_name}/{identity.AgentConfig.schema_file}"
    )

    # Create Agent for Amazon Bedrock
    bedrock_agent = identity.session.client("bedrock-agent")
    response = bedrock_agent.create_agent(
        agentName=identity.ChaliceConfig.app_name,
        agentResourceRoleArn=identity.agents_role_arn,
        instruction=identity.AgentConfig.instructions,
        description=identity.AgentConfig.description,
        idleSessionTTLInSeconds=identity.AgentConfig.idle_session_ttl_in_seconds,
        foundationModel=identity.AgentConfig.foundation_model,
    )

    # Get Created Agent Id
    agent_id = response["agent"]["agentId"]
    print(f"- Created agents for amazon bedrock : {agent_id}")

    # Wait for creating agent
    while True:
        current_agent = read_current_agent_info(identity, bedrock_agent)
        if current_agent is None:
            print("Failed to create agent")
            return
        if current_agent.agent_status == "CREATING":
            time.sleep(5)
        else:
            # Success to create agent
            break

    # Create Agent Action Group
    bedrock_agent.create_agent_action_group(
        agentId=agent_id,
        agentVersion=identity.AgentConfig.agent_version,
        actionGroupName=identity.AgentConfig.agent_action_name,
        description=identity.AgentConfig.description,
        actionGroupExecutor={"lambda": identity.lambda_arn},
        apiSchema={
            "s3": {
                "s3BucketName": identity.bucket_name,
                "s3ObjectKey": identity.AgentConfig.schema_file,
            }
        },
        actionGroupState="ENABLED",
    )
    print("- Created agent action group")

    # Add Permission to Lambda Function for Execute from Agent
    identity.session.client("lambda").add_permission(
        Action="lambda:InvokeFunction",
        FunctionName=identity.lambda_function_name,
        Principal="bedrock.amazonaws.com",
        SourceArn=identity.agent_id_to_arn(agent_id),
        StatementId="amazon-bedrock-agent",
    )
    print(f"- Added permission to lambda function : {identity.lambda_function_name}")

    # Finished Message
    print("completed")


def sync():
    """
    Command : sync

    Sync local LLM Message to cloud.
    """
    # Read config
    identity = read_identity()

    # Create Agent for Amazon Bedrock Client
    bedrock_agent = identity.session.client("bedrock-agent")

    print("Start : Sync")

    # Upload OpenAPI Schema File
    bucket = identity.session.resource("s3").Bucket(identity.bucket_name)
    with io.BytesIO(json.dumps(spec.to_dict()).encode("utf-8")) as fp:
        bucket.upload_fileobj(fp, identity.AgentConfig.schema_file)
    print(
        f"- Uploaded OpenAPI schema file to {identity.bucket_name}/{identity.AgentConfig.schema_file}"
    )

    # Get Current Agent Setting
    agent_info = read_current_agent_info(identity, bedrock_agent)
    if (agent_info is None) or len(agent_info.action_group_id) == 0:
        print("not found agent")
        return

    response = bedrock_agent.get_agent_action_group(
        agentId=agent_info.agent_id,
        agentVersion=identity.AgentConfig.agent_version,
        actionGroupId=agent_info.action_group_id,
    )
    print(f"- Get current agent : {agent_info.agent_id} : {agent_info.action_group_id}")

    # Rewrite Agent, sync current setting.
    bedrock_agent.update_agent_action_group(
        agentId=agent_info.agent_id,
        agentVersion=response["agentActionGroup"]["agentVersion"],
        actionGroupId=response["agentActionGroup"]["actionGroupId"],
        actionGroupName=response["agentActionGroup"]["actionGroupName"],
        description=response["agentActionGroup"]["description"],
        actionGroupExecutor={
            "lambda": response["agentActionGroup"]["actionGroupExecutor"]["lambda"]
        },
        actionGroupState="ENABLED",
        apiSchema={
            "s3": {
                "s3BucketName": response["agentActionGroup"]["apiSchema"]["s3"][
                    "s3BucketName"
                ],
                "s3ObjectKey": response["agentActionGroup"]["apiSchema"]["s3"][
                    "s3ObjectKey"
                ],
            }
        },
    )
    print(f"- Updated agents for amazon bedrock : {agent_info.agent_id}")

    # Finished Message
    print("completed")


def delete():
    """
    Command : delete

    Delete Agent for Amazon Bedrock Resources
    """

    # Read config
    identity = read_identity()

    # Create Agent for Amazon Bedrock Client and S3 Client
    bedrock_agent = identity.session.client("bedrock-agent")
    s3 = identity.session.client("s3")

    print("Start : Delete")

    # Delete OpenAPI Schema File
    s3.delete_object(Bucket=identity.bucket_name, Key=identity.AgentConfig.schema_file)
    print(
        f"- Deleted OpenAPI schema file to {identity.bucket_name}/{identity.AgentConfig.schema_file}"
    )

    # Get Current Agent Setting
    agent_info = read_current_agent_info(identity, bedrock_agent)
    if (agent_info is None) or len(agent_info.action_group_id) == 0:
        print("not found agent")
        return

    # Delete Agent Action Group
    bedrock_agent.delete_agent_action_group(
        agentId=agent_info.agent_id,
        agentVersion=identity.AgentConfig.agent_version,
        actionGroupId=agent_info.action_group_id,
        skipResourceInUseCheck=True,
    )
    print("- Deleted agent action group")

    # Delete Agent
    bedrock_agent.delete_agent(agentId=agent_info.agent_id, skipResourceInUseCheck=True)
    print(f"- Deleted agents for amazon bedrock : {agent_info.agent_id}")

    # Delete CloudFormation Stack
    cfn = identity.session.client("cloudformation")
    cfn.delete_stack(StackName=identity.stack_name)
    print(f"- Start to delete stack... : {identity.stack_name}")

    # Wait for complete
    waiter = cfn.get_waiter("stack_delete_complete")
    waiter.wait(StackName=identity.stack_name)
    print(f"- Deleted stack : {identity.stack_name}")

    # Finished Message
    print("completed")


def show():
    """
    Command : show

    Show OpenAPI Schema
    """
    print(json.dumps(spec.to_dict(), indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "init":
        init()
    if sys.argv[1] == "sync":
        sync()
    if sys.argv[1] == "delete":
        delete()
    if sys.argv[1] == "show":
        show()
