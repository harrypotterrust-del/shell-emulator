#!/bin/sh
# Запуск скрипта с командой exit: оставшиеся строки не выполняются
# и REPL не открывается.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs_examples/minimal" \
               --script "$ROOT/startup/stage2_exit.txt"
