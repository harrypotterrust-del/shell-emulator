"""Встроенные команды эмулятора.

Каждая команда - функция ``(shell, args) -> Optional[str]``: получает
экземпляр оболочки и список аргументов, возвращает текст для вывода
(``None`` - выводить нечего). Об ошибке команда сообщает исключением
``CommandError``. Команды ``ls`` и ``cd`` находятся в модуле
``navigation``, ``head`` и ``uniq`` - в модуле ``textcmds``.
"""

from emulator.errors import CommandError, ExitRequest
from emulator.navigation import cmd_cd, cmd_ls
from emulator.textcmds import cmd_head, cmd_uniq
from emulator.vfs import format_tree

MAX_EXIT_ARGS = 1
EXIT_CODE_LIMIT = 256


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


def cmd_vfs_tree(shell, args):
    """Служебная команда: показать дерево загруженной VFS."""
    if args:
        raise CommandError("too many arguments")
    if shell.vfs is None:
        raise CommandError("VFS не загружена")
    return format_tree(shell.vfs)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "head": cmd_head,
    "uniq": cmd_uniq,
    "exit": cmd_exit,
    "vfs-tree": cmd_vfs_tree,
}
