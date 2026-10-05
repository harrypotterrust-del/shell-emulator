"""Тесты разбора параметров командной строки."""

from emulator.config import NOT_SET, Config, format_config, parse_args

VFS = "/tmp/vfs"
SCRIPT = "/tmp/start.txt"


def test_defaults_are_empty():
    """Без аргументов оба параметра не заданы."""
    config = parse_args([])
    assert config == Config(vfs_path=None, script_path=None)


def test_both_parameters():
    """Разбираются оба параметра командной строки."""
    config = parse_args(["--vfs", VFS, "--script", SCRIPT])
    assert config.vfs_path == VFS
    assert config.script_path == SCRIPT


def test_only_script():
    """Параметры независимы: можно задать лишь один из них."""
    config = parse_args(["--script", SCRIPT])
    assert config.vfs_path is None
    assert config.script_path == SCRIPT


def test_debug_output_shows_values():
    """Отладочный вывод содержит значения заданных параметров."""
    text = format_config(parse_args(["--vfs", VFS, "--script", SCRIPT]))
    assert VFS in text
    assert SCRIPT in text


def test_debug_output_marks_missing():
    """Незаданный параметр помечается в отладочном выводе."""
    text = format_config(parse_args(["--vfs", VFS]))
    assert NOT_SET in text
