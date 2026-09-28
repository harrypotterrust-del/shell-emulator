"""Встроенные команды эмулятора.

Каждая команда — функция ``(shell, args) -> str``: получает экземпляр
оболочки и список аргументов, возвращает текст для вывода. Об ошибке
команда сообщает исключением ``CommandError``.
"""

MAX_CD_ARGS = 1
MAX_EXIT_ARGS = 1
EXIT_CODE_LIMIT = 256


class CommandError(Exception):
    """Ошибка выполнения команды (например, неверные аргументы)."""


class ExitRequest(Exception):
    """Запрос на завершение работы эмулятора с кодом возврата."""

    def __init__(self, code):
        """Сохранить код возврата ``code``."""
        super().__init__(code)
        self.code = code


def format_stub(name, args):
    """Сформировать вывод команды-заглушки: имя и список аргументов."""
    return f"{name}: args={args!r}"


def cmd_ls(shell, args):
    """Заглушка ``ls``: вывести имя команды и аргументы."""
    return format_stub("ls", args)


def cmd_cd(shell, args):
    """Заглушка ``cd``: проверить число аргументов и вывести их."""
    if len(args) > MAX_CD_ARGS:
        raise CommandError("too many arguments")
    return format_stub("cd", args)


def cmd_exit(shell, args):
    """Завершить работу эмулятора: ``exit [код]``."""
    if len(args) > MAX_EXIT_ARGS:
        raise CommandError("too many arguments")
    code = 0
    if args:
        try:
            code = int(args[0]) % EXIT_CODE_LIMIT
        except ValueError:
            raise CommandError(
                f"{args[0]}: numeric argument required") from None
    raise ExitRequest(code)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}
