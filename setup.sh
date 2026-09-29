#!/usr/bin/env bash

set -euo pipefail

mkdir -p images db log var/compressed

if [ -z "$(ls -A images)" ]; then
    cp -R sample_images/. images/
fi

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example; fill in its values before starting the bot."
fi
