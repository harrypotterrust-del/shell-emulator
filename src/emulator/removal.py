"""Команда ``rm``: удаление файлов и папок из VFS.

Удаляются только узлы дерева в оперативной памяти. Исходная директория
на диске не изменяется: после перезапуска эмулятора всё возвращается.
"""

from emulator.errors import CommandError, finish
from emulator.navigation import child_label
from emulator.options import parse_options
from emulator.paths import (CURRENT, IS_A_DIRECTORY, PARENT, SEPARATOR,
                            PathError, resolve)

RM_SPEC = {"r": False, "R": False, "d": False, "f": False, "v": False}
NOT_EMPTY = "Directory not empty"
DOT_NAMES = (CURRENT, PARENT)


def last_segment(operand):
    """Вернуть последнее имя в записи пути (``docs/..`` даёт ``..``)."""
    parts = [part for part in operand.split(SEPARATOR) if part]
    return parts[-1] if parts else ""


def is_inside(cwd, names):
    """Проверить, что ``cwd`` совпадает с путём ``names`` или лежит в нём."""
    return cwd[:len(names)] == names


def removed_lines(label, node):
    """Построить строки ``-v``: сначала вложенное, потом сама папка."""
    if not node.is_dir:
        return [f"removed '{label}'"]
    lines = []
    for name in sorted(node.children):
        lines += removed_lines(child_label(label, name),
                               node.children[name])
    lines.append(f"removed directory '{label}'")
    return lines


def check_removable(shell, operand, place, flags):
    """Убедиться, что узел можно удалить; иначе возбудить ``CommandError``.

    Нельзя удалять корень, а также текущую папку и всех её родителей:
    оболочка осталась бы в несуществующем месте.
    """
    if not place.names:
        raise CommandError(
            f"refusing to remove the root directory '{operand}'")
    recursive = flags.get("r") or flags.get("R")
    if place.node.is_dir and not recursive:
        if not flags.get("d"):
            raise CommandError(
                f"cannot remove '{operand}': {IS_A_DIRECTORY}")
        if place.node.children:
            raise CommandError(f"cannot remove '{operand}': {NOT_EMPTY}")
    if is_inside(shell.cwd, place.names):
        raise CommandError(f"cannot remove '{operand}': "
                           "it is or contains the current directory")


def remove_operand(shell, operand, flags):
    """Удалить узел по одному операнду; вернуть строки вывода ``-v``.

    С ``-f`` несуществующий путь молча пропускается.
    """
    if last_segment(operand) in DOT_NAMES:
        raise CommandError("refusing to remove '.' or '..' directory: "
                           f"skipping '{operand}'")
    try:
        place = resolve(shell.root, shell.cwd, operand)
    except PathError as exc:
        if flags.get("f"):
            return []
        raise CommandError(f"cannot remove '{operand}': {exc}") from None
    check_removable(shell, operand, place, flags)
    lines = []
    if flags.get("v"):
        lines = removed_lines(operand.rstrip(SEPARATOR), place.node)
    del place.parent.children[place.names[-1]]
    return lines


def cmd_rm(shell, args):
    """``rm [-r] [-f] [-v] [-d] путь...`` - удалить файлы и папки.

    ``-r`` (``-R``) удаляет папки с содержимым, ``-d`` - пустые папки,
    ``-f`` не сообщает об отсутствующих путях, ``-v`` печатает каждое
    удаление. Операнды обрабатываются по очереди; ошибка одного не
    мешает остальным.
    """
    flags, operands = parse_options(args, RM_SPEC)
    if not operands:
        if flags.get("f"):
            return None
        raise CommandError("missing operand")
    lines, errors = [], []
    for operand in operands:
        try:
            lines += remove_operand(shell, operand, flags)
        except CommandError as exc:
            errors.append(str(exc))
    return finish("\n".join(lines) if lines else None, errors)
