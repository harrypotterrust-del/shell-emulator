"""Разбор путей и поиск узлов в виртуальной файловой системе.

Корень VFS одновременно служит домашней папкой: ``~``, ``~/docs`` и
``/docs`` - один и тот же путь. Текущая папка хранится как кортеж имён
папок от корня, поэтому ``()`` - это корень.
"""

from collections import namedtuple

SEPARATOR = "/"
HOME_MARK = "~"
CURRENT = "."
PARENT = ".."
NOT_FOUND = "No such file or directory"
NOT_A_DIRECTORY = "Not a directory"
IS_A_DIRECTORY = "Is a directory"

Location = namedtuple("Location", "names node parent")


class PathError(Exception):
    """Путь не найден или не подходит для операции."""


def split_start(path):
    """Определить начало пути: вернуть (от корня?, остаток пути)."""
    if path == HOME_MARK or path.startswith(HOME_MARK + SEPARATOR):
        return True, path[len(HOME_MARK):]
    return path.startswith(SEPARATOR), path


def step(chain, names, segment):
    """Сдвинуть позицию на один сегмент пути.

    ``chain`` - узлы от корня до текущего, ``names`` - имена папок.
    """
    if not segment:
        return
    if not chain[-1].is_dir:
        raise PathError(NOT_A_DIRECTORY)
    if segment == CURRENT:
        return
    if segment == PARENT:
        if names:
            names.pop()
            chain.pop()
        return
    child = chain[-1].children.get(segment)
    if child is None:
        raise PathError(NOT_FOUND)
    names.append(segment)
    chain.append(child)


def resolve(root, cwd, path):
    """Найти узел по пути ``path``, отсчитывая от папки ``cwd``.

    Поддерживаются ``.``, ``..`` (выше корня подняться нельзя),
    абсолютные пути и ``~``. Возвращает ``Location``: имена папок от
    корня, сам узел и его родитель (у корня родитель - он сам).
    Если пути нет, возбуждает ``PathError``.
    """
    from_root, rest = split_start(path)
    chain, names = [root], []
    if not from_root:
        for name in cwd:
            step(chain, names, name)
    for segment in rest.split(SEPARATOR):
        step(chain, names, segment)
    if path.endswith(SEPARATOR) and not chain[-1].is_dir:
        raise PathError(NOT_A_DIRECTORY)
    return Location(tuple(names), chain[-1], chain[-2:][0])


def format_cwd(names):
    """Записать текущую папку для приглашения: ``~`` или ``~/a/b``."""
    return HOME_MARK + "".join(SEPARATOR + name for name in names)
