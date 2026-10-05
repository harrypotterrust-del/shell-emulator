"""Точка входа эмулятора: ``python -m emulator``."""

import contextlib
import importlib
import sys

from emulator.config import format_config, parse_args
from emulator.script import run_script
from emulator.shell import Shell


def enable_line_editing():
    """Подключить readline: стрелки и история ввода, если модуль есть."""
    with contextlib.suppress(ImportError):
        importlib.import_module("readline")


def main(argv=None):
    """Запустить эмулятор: параметры, стартовый скрипт, затем REPL."""
    config = parse_args(argv)
    print(format_config(config))
    enable_line_editing()
    shell = Shell(config=config)
    if config.script_path:
        run_script(shell, config.script_path)
    if shell.running:
        return shell.run_repl()
    return shell.last_status


if __name__ == "__main__":
    sys.exit(main())
