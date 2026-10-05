#!/bin/sh
# Запуск только с параметром --vfs.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs_examples/minimal"
