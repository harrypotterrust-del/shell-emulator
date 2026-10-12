#!/bin/sh
# Минимальная VFS: один файл в корне.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs_examples/minimal" \
               --script "$ROOT/startup/stage3_all.txt"
