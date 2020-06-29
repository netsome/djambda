#!/usr/bin/env bash
set -e

STAGES=("base" "prod" "test" "dev")

for STAGE in ${STAGES[*]}
do
  pip-compile ${ALLOW_UNSAFE} --generate-hashes --upgrade requirements/${STAGE}.in
done
