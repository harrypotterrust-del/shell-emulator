"""Команды просмотра и смены каталога: ``ls`` и ``cd``.

Обе команды работают с VFS в памяти и ничего не меняют на диске.
"""

from operator import itemgetter

from emulator.errors import CommandError, finish
from emulator.options import parse_options
from emulator.paths import (CURRENT, HOME_MARK, NOT_A_DIRECTORY, PARENT,
                            SEPARATOR, Location, PathError, format_cwd,
                            resolve)

LS_SPEC = {"a": False, "l": False, "R": False}
MAX_CD_ARGS = 1
SINGLE = 1
BLOCK_GAP = "\n\n"
OLDPWD_MARK = "-"
HIDDEN_MARK = "."
DIR_TYPE = "d"
FILE_TYPE = "-"
DOT_ENTRIES = (CURRENT, PARENT)
LABEL = itemgetter(0)


def entry_size(node):
    """Размер записи: длина файла; у папки размера нет - 0."""
    return 0 if node.is_dir else len(node.data)


def format_entries(entries, long_format):
    """Построить строки для записей ``(имя, узел)``.

    Обычный вид - по одному имени в строке. Подробный (``-l``): тип
    (``d`` - папка, ``-`` - файл), размер в байтах и имя.
    """
    if not long_format:
        return [name for name, _ in entries]
    width = max((len(str(entry_size(node))) for _, node in entries),
                default=0)
    return [
        f"{DIR_TYPE if node.is_dir else FILE_TYPE} "
        f"{entry_size(node):>{width}} {name}"
        for name, node in entries
    ]


def dir_entries(node, parent, show_all):
    """Вернуть записи папки по именам; скрытые - только с ``-a``.

    С ``-a`` добавляются записи ``.`` и ``..``.
    """
    entries = list(node.children.items())
    if show_all:
        entries += [(CURRENT, node), (PARENT, parent)]
    else:
        entries = [(name, child) for name, child in entries
                   if not name.startswith(HIDDEN_MARK)]
    return sorted(entries, key=LABEL)


def format_block(label, lines, titled):
    """Собрать блок вывода папки; с заголовком ``путь:`` при ``titled``."""
    body = "\n".join(lines)
    if not titled:
        return body
    return f"{label}:\n{body}" if body else f"{label}:"


def child_label(label, name):
    """Составить подпись вложенной папки для рекурсивного вывода."""
    return label.rstrip(SEPARATOR) + SEPARATOR + name


def list_dir(label, place, flags, titled):
    """Вернуть блоки вывода папки, а с ``-R`` и всех её подпапок."""
    entries = dir_entries(place.node, place.parent, flags.get("a"))
    blocks = [format_block(label, format_entries(entries, flags.get("l")),
                           titled)]
    if flags.get("R"):
        for name, child in entries:
            if child.is_dir and name not in DOT_ENTRIES:
                sub = Location(place.names + (name,), child, place.node)
                blocks += list_dir(child_label(label, name), sub, flags,
                                   titled)
    return blocks


def locate_operands(shell, operands):
    """Найти узлы для операндов ``ls``.

    Возвращает файлы, папки (оба списка из пар ``(подпись, место)``,
    упорядоченные по подписи) и тексты ошибок.
    """
    files, dirs, errors = [], [], []
    for operand in operands:
        try:
            place = resolve(shell.root, shell.cwd, operand)
        except PathError as exc:
            errors.append(f"cannot access '{operand}': {exc}")
            continue
        (dirs if place.node.is_dir else files).append((operand, place))
    return sorted(files, key=LABEL), sorted(dirs, key=LABEL), errors


def cmd_ls(shell, args):
    """``ls [-a] [-l] [-R] [путь...]`` - содержимое папок и файлы.

    Без операндов выводится текущая папка. Если путей несколько или
    указан ``-R``, у каждой папки печатается заголовок ``путь:``.
    """
    flags, operands = parse_options(args, LS_SPEC)
    files, dirs, errors = locate_operands(shell, operands or [CURRENT])
    titled = len(operands) > SINGLE or bool(flags.get("R"))
    blocks = []
    if files:
        entries = [(label, place.node) for label, place in files]
        blocks.append("\n".join(format_entries(entries, flags.get("l"))))
    for label, place in dirs:
        blocks += list_dir(label, place, flags, titled)
    text = BLOCK_GAP.join(block for block in blocks if block) or None
    return finish(text, errors)


def resolve_dir(shell, path):
    """Найти папку по пути или сообщить, что это невозможно."""
    try:
        place = resolve(shell.root, shell.cwd, path)
    except PathError as exc:
        raise CommandError(f"{path}: {exc}") from None
    if not place.node.is_dir:
        raise CommandError(f"{path}: {NOT_A_DIRECTORY}")
    return place


def go_back(shell):
    """Вернуться в прошлую папку (``cd -``) и вывести её путь."""
    if shell.oldpwd is None:
        raise CommandError("OLDPWD not set")
    target = format_cwd(shell.oldpwd)
    shell.change_dir(resolve_dir(shell, target).names)
    return target


def cmd_cd(shell, args):
    """``cd [путь]`` - сменить текущую папку.

    Без аргумента - переход в корень (домашнюю папку), ``cd -`` - в
    предыдущую папку.
    """
    _, operands = parse_options(args, {})
    if len(operands) > MAX_CD_ARGS:
        raise CommandError("too many arguments")
    target = operands[0] if operands else HOME_MARK
    if target == OLDPWD_MARK:
        return go_back(shell)
    shell.change_dir(resolve_dir(shell, target).names)
    return None
