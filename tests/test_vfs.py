"""Тесты виртуальной файловой системы в памяти."""

import io
import os

import pytest

from emulator.shell import Shell
from emulator.vfs import (MAX_FILE_SIZE, Node, VfsError, count_nodes,
                          format_tree, load_vfs)

BINARY = bytes(range(32))
TEXT = "строка\n"
MISSING = "нет-такой-папки"


def make_tree(root):
    """Создать на диске пример VFS из трёх уровней."""
    (root / "readme.txt").write_text(TEXT, encoding="utf-8")
    (root / "data.bin").write_bytes(BINARY)
    docs = root / "docs"
    (docs / "notes").mkdir(parents=True)
    (docs / "guide.txt").write_text(TEXT, encoding="utf-8")
    (docs / "notes" / "plan.txt").write_text(TEXT, encoding="utf-8")
    return root


def make_shell(vfs=None):
    """Создать оболочку с перехватом вывода."""
    return Shell(env={}, out=io.StringIO(), err=io.StringIO(), vfs=vfs)


def test_loads_whole_tree(tmp_path):
    """Загружаются все уровни вложенности."""
    root = load_vfs(str(make_tree(tmp_path)))
    assert set(root.children) == {"readme.txt", "data.bin", "docs"}
    notes = root.children["docs"].children["notes"]
    assert "plan.txt" in notes.children


def test_binary_file_is_kept_as_bytes(tmp_path):
    """Двоичный файл загружается без искажений."""
    root = load_vfs(str(make_tree(tmp_path)))
    assert root.children["data.bin"].data == BINARY


def test_text_file_content(tmp_path):
    """Содержимое текстового файла доступно в памяти."""
    root = load_vfs(str(make_tree(tmp_path)))
    data = root.children["readme.txt"].data
    assert data.decode("utf-8") == TEXT


def test_source_directory_is_not_modified(tmp_path):
    """Загрузка не изменяет исходную директорию на диске."""
    make_tree(tmp_path)
    before = sorted(os.walk(tmp_path))
    load_vfs(str(tmp_path))
    assert sorted(os.walk(tmp_path)) == before


def test_missing_path(tmp_path):
    """Несуществующий путь: ошибка загрузки VFS."""
    with pytest.raises(VfsError):
        load_vfs(str(tmp_path / MISSING))


def test_source_must_be_directory(tmp_path):
    """Обычный файл вместо директории: ошибка загрузки VFS."""
    source = tmp_path / "readme.txt"
    source.write_text(TEXT, encoding="utf-8")
    with pytest.raises(VfsError):
        load_vfs(str(source))


def test_too_large_file(tmp_path):
    """Файл больше допустимого размера: ошибка загрузки VFS."""
    (tmp_path / "big.bin").write_bytes(b"\0" * (MAX_FILE_SIZE + 1))
    with pytest.raises(VfsError):
        load_vfs(str(tmp_path))


def test_symlink_is_skipped(tmp_path):
    """Символические ссылки пропускаются: они могут вести наружу."""
    make_tree(tmp_path)
    os.symlink(tmp_path / "readme.txt", tmp_path / "link.txt")
    root = load_vfs(str(tmp_path))
    assert "link.txt" not in root.children


def test_count_nodes(tmp_path):
    """Сводка считает папки, файлы и суммарный размер."""
    root = load_vfs(str(make_tree(tmp_path)))
    dirs, files, size = count_nodes(root)
    assert (dirs, files) == (2, 4)
    assert size == len(BINARY) + 3 * len(TEXT.encode("utf-8"))


def test_format_tree_shows_nesting(tmp_path):
    """Дерево показывает вложенные папки и размеры файлов."""
    text = format_tree(load_vfs(str(make_tree(tmp_path))))
    assert "docs/" in text
    assert "plan.txt" in text
    assert f"({len(BINARY)} Б)" in text


def test_vfs_tree_command(tmp_path):
    """Команда vfs-tree выводит дерево загруженной VFS."""
    shell = make_shell(load_vfs(str(make_tree(tmp_path))))
    assert shell.execute("vfs-tree")
    assert "docs/" in shell.out.getvalue()


def test_vfs_tree_without_vfs():
    """Без загруженной VFS команда vfs-tree сообщает об ошибке."""
    shell = make_shell()
    assert not shell.execute("vfs-tree")
    assert "VFS не загружена" in shell.err.getvalue()


def test_vfs_tree_rejects_arguments():
    """Команда vfs-tree не принимает аргументов."""
    shell = make_shell(Node(name="root", is_dir=True))
    assert not shell.execute("vfs-tree лишний")
    assert "too many arguments" in shell.err.getvalue()
