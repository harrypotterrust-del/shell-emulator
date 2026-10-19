#!/bin/sh
# Плоская VFS: несколько файлов в одной папке.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs_examples/flat" \
               --script "$ROOT/startup/stage3_all.txt"
