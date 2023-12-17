#!/bin/bash

docker run -it --rm \
    -v ${PWD}/${TARGET}/sample-app.py:/app/app.py \
    -v ${PWD}/${TARGET}/.chalice:/app/.chalice \
    -v ${PWD}/common/example/chalicelib:/app/chalicelib \
    -v ${PWD}/../chalice_spec:/app/vendor/chalice_spec \
    -p 8000:8000 \
    --env-file ${PWD}/.env \
    --entrypoint "/usr/local/bin/chalice" \
    $CHALICE_SPEC_IMAGE $@
