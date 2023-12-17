#!/bin/bash

source ./0.config-script.sh
docker build -t $CHALICE_SPEC_IMAGE .
