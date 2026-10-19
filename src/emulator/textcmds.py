"""Команды чтения файлов VFS: ``head`` и ``uniq``.

Без операндов настоящие утилиты читают стандартный ввод. В эмуляторе
конвейеров нет, поэтому файл указывать обязательно.
"""

from itertools import groupby

from emulator.errors import CommandError, finish
from emulator.options import parse_options
from emulator.paths import IS_A_DIRECTORY, PathError, resolve

HEAD_SPEC = {"n": True, "c": True}
UNIQ_SPEC = {"c": False, "d": False, "u": False, "i": False}
DEFAULT_LINES = 10
COUNT_WIDTH = 7
SINGLE = 1
NEWLINE = "\n"
RAW_NEWLINE = b"\n"
SECTION_GAP = "\n\n"
LINES = "lines"
BYTES = "bytes"


def load_file(shell, path):
    """Вернуть содержимое файла в виде байтов.

    Возбуждает ``PathError``, если пути нет или это папка.
    """
    node = resolve(shell.root, shell.cwd, path).node
    if node.is_dir:
        raise PathError(IS_A_DIRECTORY)
    return node.data


def decode(data):
    """Превратить байты в текст; нечитаемые байты заменяются на «?»."""
    return data.decode("utf-8", errors="replace")


def parse_count(value, unit):
    """Проверить, что значение ``-n``/``-c`` - неотрицательное число."""
    if not (value.isascii() and value.isdigit()):
        raise CommandError(f"invalid number of {unit}: '{value}'")
    return int(value)


def head_limit(flags):
    """Определить, сколько выводить: вернуть (число, единица счёта).

    Единица - строки (``-n``, по умолчанию 10) или байты (``-c``).
    """
    if "n" in flags and "c" in flags:
        raise CommandError("can't combine line and byte counts")
    if "c" in flags:
        return parse_count(flags["c"], BYTES), BYTES
    if "n" in flags:
        return parse_count(flags["n"], LINES), LINES
    return DEFAULT_LINES, LINES


def head_lines(data, count):
    """Взять первые ``count`` строк; ``None``, если брать нечего."""
    pieces = data.split(RAW_NEWLINE)
    if not pieces[-1]:
        pieces.pop()
    chosen = pieces[:count]
    if not chosen:
        return None
    return decode(RAW_NEWLINE.join(chosen))


def head_bytes(data, count):
    """Взять первые ``count`` байтов; ``None``, если брать нечего."""
    chunk = data[:count]
    if not chunk:
        return None
    text = decode(chunk)
    return text[:-1] if text.endswith(NEWLINE) else text


def head_section(path, body, titled):
    """Оформить вывод одного файла; при ``titled`` - с заголовком."""
    if not titled:
        return body
    header = f"==> {path} <=="
    return header if body is None else f"{header}{NEWLINE}{body}"


def head_error(path, exc):
    """Сформировать сообщение об ошибке чтения для ``head``."""
    if str(exc) == IS_A_DIRECTORY:
        return f"error reading '{path}': {exc}"
    return f"cannot open '{path}' for reading: {exc}"


def cmd_head(shell, args):
    """``head [-n N | -c N] файл...`` - начало файлов.

    По умолчанию выводятся первые 10 строк. Для нескольких файлов
    перед каждым печатается заголовок ``==> имя <==``.
    """
    flags, operands = parse_options(args, HEAD_SPEC)
    count, unit = head_limit(flags)
    if not operands:
        raise CommandError("missing file operand")
    take = head_lines if unit == LINES else head_bytes
    titled = len(operands) > SINGLE
    sections, errors = [], []
    for path in operands:
        try:
            body = take(load_file(shell, path), count)
        except PathError as exc:
            errors.append(head_error(path, exc))
            continue
        sections.append(head_section(path, body, titled))
    shown = [section for section in sections if section is not None]
    return finish(SECTION_GAP.join(shown) if shown else None, errors)


def group_lines(lines, ignore_case):
    """Объединить подряд идущие одинаковые строки: ``[(строка, число)]``.

    Из каждой группы берётся первая строка.
    """
    key = str.casefold if ignore_case else None
    groups = []
    for _, run in groupby(lines, key=key):
        items = list(run)
        groups.append((items[0], len(items)))
    return groups


def select_groups(groups, flags):
    """Отобрать группы по ``-d`` (повторяющиеся) и ``-u`` (одиночные)."""
    if flags.get("d"):
        groups = [group for group in groups if group[1] > SINGLE]
    if flags.get("u"):
        groups = [group for group in groups if group[1] == SINGLE]
    return groups


def format_groups(groups, with_count):
    """Построить строки вывода; с ``-c`` перед строкой стоит счётчик."""
    if with_count:
        return [f"{count:>{COUNT_WIDTH}} {line}" for line, count in groups]
    return [line for line, _ in groups]


def split_lines(data):
    """Разбить содержимое файла на строки без завершающего перевода."""
    lines = decode(data).split(NEWLINE)
    if not lines[-1]:
        lines.pop()
    return lines


def cmd_uniq(shell, args):
    """``uniq [-c] [-d] [-u] [-i] файл`` - убрать повторы подряд.

    ``-c`` - считать повторы, ``-d`` - показать только повторяющиеся
    строки, ``-u`` - только неповторяющиеся, ``-i`` - не различать
    регистр. Сравниваются только соседние строки.
    """
    flags, operands = parse_options(args, UNIQ_SPEC)
    if not operands:
        raise CommandError("missing file operand")
    if len(operands) > SINGLE:
        raise CommandError(f"extra operand '{operands[SINGLE]}'")
    try:
        data = load_file(shell, operands[0])
    except PathError as exc:
        raise CommandError(f"{operands[0]}: {exc}") from None
    groups = group_lines(split_lines(data), flags.get("i"))
    lines = format_groups(select_groups(groups, flags), flags.get("c"))
    return NEWLINE.join(lines) if lines else None
