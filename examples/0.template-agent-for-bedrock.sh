#!/bin/bash

docker run -it --rm \
    -v ${PWD}/${TARGET}/sample-app.py:/app/app.py \
    -v ${PWD}/${TARGET}/.chalice:/app/.chalice \
    -v ${PWD}/${TARGET}/management.py:/app/management.py \
    -v ${PWD}/${TARGET}/template.yaml:/app/template.yaml \
    -v ${PWD}/common/example/chalicelib:/app/chalicelib \
    -v ${PWD}/../chalice_spec:/app/chalice_spec \
    --env-file ${PWD}/.env \
    --entrypoint "/usr/local/bin/python" \
    $CHALICE_SPEC_IMAGE "management.py" $@
