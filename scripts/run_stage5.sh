#!/bin/sh
# Этап 5: сценарий с командой rm на VFS vfs_examples/rm_demo. После
# выхода из эмулятора выводится физическая директория: файлы на диске
# остаются на месте, так как rm изменяет только VFS в памяти.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --vfs "$ROOT/vfs_examples/rm_demo" \
               --script "$ROOT/startup/stage5_all.txt"
echo
echo "Физическая директория после работы эмулятора:"
(cd "$ROOT" && find vfs_examples/rm_demo | sort)
