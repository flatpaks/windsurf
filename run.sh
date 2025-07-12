#!/usr/bin/env bash
export ELECTRON_RUN_AS_NODE=1
exec /app/share/windsurf/windsurf /app/share/windsurf/resources/app/out/cli.js "$@"
