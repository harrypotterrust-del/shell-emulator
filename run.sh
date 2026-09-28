#!/bin/sh
# Запуск эмулятора из любой папки: ./run.sh [--vfs PATH] [--script PATH]
ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$ROOT/src" exec python3 -m emulator "$@"
