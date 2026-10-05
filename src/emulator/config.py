"""Параметры запуска эмулятора и их отладочный вывод."""

import argparse
from dataclasses import dataclass

NOT_SET = "(не задан)"
CONFIG_HEADER = "=== Параметры эмулятора ==="
CONFIG_FOOTER = "=" * len(CONFIG_HEADER)


@dataclass
class Config:
    """Параметры командной строки эмулятора."""

    vfs_path: str | None = None
    script_path: str | None = None


def build_parser():
    """Создать разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор командной оболочки UNIX-подобной ОС.",
    )
    parser.add_argument("--vfs", dest="vfs_path", metavar="PATH",
                        help="путь к физическому расположению VFS")
    parser.add_argument("--script", dest="script_path", metavar="PATH",
                        help="путь к стартовому скрипту эмулятора")
    return parser


def parse_args(argv=None):
    """Разобрать аргументы командной строки в ``Config``.

    ``argv`` — список аргументов без имени программы; по умолчанию
    берутся настоящие аргументы процесса.
    """
    args = build_parser().parse_args(argv)
    return Config(vfs_path=args.vfs_path, script_path=args.script_path)


def format_config(config):
    """Сформировать отладочный вывод всех заданных параметров."""
    lines = [
        CONFIG_HEADER,
        f"VFS:    {config.vfs_path or NOT_SET}",
        f"Script: {config.script_path or NOT_SET}",
        CONFIG_FOOTER,
    ]
    return "\n".join(lines)
