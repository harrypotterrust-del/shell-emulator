#!/bin/sh
# Ошибка загрузки VFS: указанной директории не существует.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs_examples/нет-такой-папки"
