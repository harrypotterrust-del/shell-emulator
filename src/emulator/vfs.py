"""Виртуальная файловая система, размещаемая в оперативной памяти.

Источником VFS является директория на диске пользователя. Она
читается один раз при запуске, после чего все операции выполняются
только в памяти: исходная директория не изменяется.
"""

import os
from dataclasses import dataclass, field

MAX_FILE_SIZE = 1 << 20
MAX_DEPTH = 16
BRANCH = "|-- "
LAST_BRANCH = "`-- "
PIPE = "|   "
SPACE = "    "


class VfsError(Exception):
    """Ошибка загрузки виртуальной файловой системы."""


@dataclass
class Node:
    """Узел VFS: файл или папка.

    Содержимое файла хранится в виде байтов, поэтому двоичные данные
    загружаются без искажений. У папки заполнено поле ``children``.
    """

    name: str
    is_dir: bool = False
    data: bytes = b""
    children: dict = field(default_factory=dict)


def read_file(path):
    """Прочитать файл в память, проверив его размер."""
    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise VfsError(f"{path}: файл больше {MAX_FILE_SIZE} байт")
    try:
        with open(path, "rb") as source:
            return source.read()
    except OSError as exc:
        raise VfsError(f"{path}: {exc.strerror}") from None


def scan_dir(path):
    """Вернуть записи директории, упорядоченные по имени."""
    try:
        with os.scandir(path) as entries:
            return sorted(entries, key=lambda entry: entry.name)
    except OSError as exc:
        raise VfsError(f"{path}: {exc.strerror}") from None


def build_entry(entry, depth):
    """Построить узел VFS для записи директории.

    Символические ссылки пропускаются: они могут вести за пределы
    источника VFS и образовывать циклы.
    """
    if entry.is_symlink():
        return None
    if entry.is_dir(follow_symlinks=False):
        return build_dir(entry.path, entry.name, depth + 1)
    return Node(name=entry.name, data=read_file(entry.path))


def build_dir(path, name, depth):
    """Рекурсивно построить узел папки и всё её содержимое."""
    if depth > MAX_DEPTH:
        raise VfsError(f"{path}: вложенность глубже {MAX_DEPTH} уровней")
    node = Node(name=name, is_dir=True)
    for entry in scan_dir(path):
        child = build_entry(entry, depth)
        if child is not None:
            node.children[child.name] = child
    return node


def load_vfs(path):
    """Загрузить VFS из директории на диске.

    Возвращает корневой узел. Если путь не существует или не является
    директорией, возбуждает ``VfsError``.
    """
    if not os.path.exists(path):
        raise VfsError(f"{path}: нет такого файла или каталога")
    if not os.path.isdir(path):
        raise VfsError(f"{path}: источник VFS должен быть каталогом")
    name = os.path.basename(os.path.abspath(path))
    return build_dir(path, name, 0)


def count_nodes(node):
    """Подсчитать папки, файлы и суммарный размер файлов в поддереве."""
    dirs, files, size = 0, 0, 0
    for child in node.children.values():
        if child.is_dir:
            sub_dirs, sub_files, sub_size = count_nodes(child)
            dirs += 1 + sub_dirs
            files += sub_files
            size += sub_size
        else:
            files += 1
            size += len(child.data)
    return dirs, files, size


def format_summary(node):
    """Сформировать сводку о загруженной VFS для отладочного вывода."""
    dirs, files, size = count_nodes(node)
    return (f"VFS загружена: корень {node.name!r}, папок: {dirs}, "
            f"файлов: {files}, байт: {size}")


def add_children(node, prefix, lines):
    """Добавить в ``lines`` строки с содержимым папки ``node``."""
    items = list(node.children.values())
    for index, child in enumerate(items):
        last = index == len(items) - 1
        mark = LAST_BRANCH if last else BRANCH
        tail = "/" if child.is_dir else f" ({len(child.data)} Б)"
        lines.append(f"{prefix}{mark}{child.name}{tail}")
        if child.is_dir:
            add_children(child, prefix + (SPACE if last else PIPE), lines)


def format_tree(node):
    """Сформировать построчное изображение дерева VFS."""
    lines = [f"{node.name}/"]
    add_children(node, "", lines)
    return "\n".join(lines)
