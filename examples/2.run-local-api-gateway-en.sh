#!/bin/bash

export TARGET=en/api-gateway
source ./0.config-script.sh
source ./0.template-call-chalice.sh local --host 0.0.0.0
