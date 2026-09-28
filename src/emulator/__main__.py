"""Точка входа эмулятора: ``python -m emulator``."""

import sys

from emulator.shell import Shell


def enable_line_editing():
    """Включить стрелки и историю ввода, если доступен модуль readline."""
    try:
        import readline  # noqa: F401
    except ImportError:
        pass


def main():
    """Запустить эмулятор в интерактивном режиме."""
    enable_line_editing()
    shell = Shell()
    return shell.run_repl()


if __name__ == "__main__":
    sys.exit(main())
