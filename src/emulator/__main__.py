"""Точка входа эмулятора: ``python -m emulator``."""

import contextlib
import importlib
import sys

from emulator.shell import Shell


def enable_line_editing():
    """Подключить readline: стрелки и история ввода, если модуль есть."""
    with contextlib.suppress(ImportError):
        importlib.import_module("readline")


def main():
    """Запустить эмулятор в интерактивном режиме."""
    enable_line_editing()
    shell = Shell()
    return shell.run_repl()


if __name__ == "__main__":
    sys.exit(main())
