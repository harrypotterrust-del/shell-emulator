"""Точка входа эмулятора: ``python -m emulator``."""

import contextlib
import importlib
import sys

from emulator.config import format_config, parse_args
from emulator.script import run_script
from emulator.shell import Shell
from emulator.vfs import VfsError, format_summary, load_vfs


def enable_line_editing():
    """Подключить readline: стрелки и история ввода, если модуль есть."""
    with contextlib.suppress(ImportError):
        importlib.import_module("readline")


def setup_vfs(shell, path):
    """Загрузить VFS в память, сообщив об ошибке загрузки.

    При ошибке эмулятор продолжает работу без VFS.
    """
    try:
        shell.vfs = load_vfs(path)
    except VfsError as exc:
        shell.error(f"vfs: {exc}")
        return False
    shell.write(format_summary(shell.vfs))
    return True


def main(argv=None):
    """Запустить эмулятор: параметры, VFS, стартовый скрипт, REPL."""
    config = parse_args(argv)
    print(format_config(config), flush=True)
    enable_line_editing()
    shell = Shell(config=config)
    if config.vfs_path:
        setup_vfs(shell, config.vfs_path)
    if config.script_path:
        run_script(shell, config.script_path)
    if shell.running:
        return shell.run_repl()
    return shell.last_status


if __name__ == "__main__":
    sys.exit(main())
