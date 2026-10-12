#!/bin/sh
# Ошибка загрузки VFS: вместо директории указан обычный файл.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs_examples/minimal/readme.txt"
