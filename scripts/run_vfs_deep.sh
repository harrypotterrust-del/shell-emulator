#!/bin/sh
# Многоуровневая VFS: четыре уровня папок и файлов.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs_examples/deep" \
               --script "$ROOT/startup/stage3_all.txt"
