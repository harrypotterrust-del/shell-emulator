#!/bin/sh
# Этап 4: демонстрационная VFS и скрипт со всеми режимами ls, cd,
# head и uniq, включая обработку ошибок.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs_examples/demo" \
               --script "$ROOT/startup/stage4_all.txt"
