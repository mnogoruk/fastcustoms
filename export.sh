#!/bin/sh

# shellcheck disable=SC2039
source .env.dev
# shellcheck disable=SC2046
export $(cut -d= -f1 .env.dev)