#!/bin/bash

export TARGET=en/agents-for-amazon-bedrock
source ./0.config-script.sh
source ./0.template-agent-for-bedrock.sh delete
source ./0.template-call-chalice.sh delete
