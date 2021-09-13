#!/bin/sh

# shellcheck disable=SC2039
source .env.dev
export $(cut -d= -f1 .env.dev)