"""Выполнение стартового скрипта эмулятора.

Скрипт выполняется построчно: на экране показывается как ввод, так и
вывод, имитируя диалог с пользователем. Ошибочная строка пропускается,
но о ней сообщается с указанием файла и номера строки.
"""

COMMENT_MARK = "#"
SKIP_NOTICE = "строка пропущена"
BAD_ENCODING = "неверная кодировка файла"


def load_lines(path):
    """Прочитать строки скрипта без символов перевода строки."""
    with open(path, encoding="utf-8") as source:
        return source.read().splitlines()


def is_skippable(line):
    """Проверить, что строка пустая или является комментарием."""
    stripped = line.strip()
    return not stripped or stripped.startswith(COMMENT_MARK)


def run_line(shell, path, number, line):
    """Выполнить строку скрипта, имитируя диалог с пользователем.

    Возвращает ``False``, если эмулятор запросил завершение работы.
    """
    shell.write(f"{shell.prompt()}{line}")
    if not shell.execute(line):
        shell.error(f"{path}:{number}: {SKIP_NOTICE}")
    return shell.running


def run_script(shell, path):
    """Выполнить стартовый скрипт, пропуская ошибочные строки.

    Возвращает ``True``, если скрипт удалось прочитать, и ``False``
    при ошибке чтения файла.
    """
    try:
        lines = load_lines(path)
    except OSError as exc:
        shell.error(f"{path}: {exc.strerror}")
        return False
    except UnicodeDecodeError:
        shell.error(f"{path}: {BAD_ENCODING}")
        return False
    for number, line in enumerate(lines, start=1):
        if is_skippable(line):
            continue
        if not run_line(shell, path, number, line):
            break
    return True
