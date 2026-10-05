#!/bin/sh
# Запуск со всеми параметрами: скрипт с ошибочными строками,
# которые пропускаются, после чего открывается REPL.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs_examples/minimal" \
               --script "$ROOT/startup/stage2_errors.txt"
