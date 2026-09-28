"""Оболочка эмулятора: приглашение, выполнение команд и цикл REPL."""

import getpass
import os
import socket
import sys

from emulator.commands import COMMANDS, CommandError, ExitRequest
from emulator.parser import ParseError, parse

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_NOT_FOUND = 127
HOME_MARK = "~"


def short_hostname():
    """Вернуть имя компьютера без доменной части (``.local``)."""
    return socket.gethostname().split(".")[0]


class Shell:
    """Эмулятор командной оболочки UNIX-подобной ОС."""

    def __init__(self, env=None, out=None, err=None):
        """Создать оболочку.

        ``env`` — переменные окружения (по умолчанию — реальные из ОС),
        ``out`` и ``err`` — потоки для вывода и сообщений об ошибках.
        """
        self.env = dict(os.environ) if env is None else env
        self.out = out if out is not None else sys.stdout
        self.err = err if err is not None else sys.stderr
        self.user = getpass.getuser()
        self.host = short_hostname()
        self.cwd = HOME_MARK
        self.running = True
        self.last_status = EXIT_SUCCESS

    def prompt(self):
        """Сформировать приглашение вида ``user@host:~$``."""
        return f"{self.user}@{self.host}:{self.cwd}$ "

    def write(self, text):
        """Вывести текст команды в стандартный вывод."""
        print(text, file=self.out)

    def error(self, message):
        """Вывести сообщение об ошибке в поток ошибок."""
        print(message, file=self.err)

    def execute(self, line):
        """Выполнить одну строку ввода.

        Возвращает ``True`` при успехе и ``False`` при ошибке.
        Код завершения сохраняется в ``last_status``.
        """
        try:
            words = parse(line, self.env)
        except ParseError as exc:
            return self.fail(f"syntax error: {exc}", EXIT_FAILURE)
        if not words:
            return True
        name, args = words[0], words[1:]
        command = COMMANDS.get(name)
        if command is None:
            return self.fail(f"{name}: command not found", EXIT_NOT_FOUND)
        return self.run_command(name, command, args)

    def run_command(self, name, command, args):
        """Запустить найденную команду и обработать её результат."""
        try:
            output = command(self, args)
        except CommandError as exc:
            return self.fail(f"{name}: {exc}", EXIT_FAILURE)
        except ExitRequest as exc:
            self.running = False
            self.last_status = exc.code
            return True
        if output:
            self.write(output)
        self.last_status = EXIT_SUCCESS
        return True

    def fail(self, message, status):
        """Сообщить об ошибке, запомнить код и вернуть ``False``."""
        self.error(message)
        self.last_status = status
        return False

    def run_repl(self, read_line=input):
        """Запустить интерактивный цикл «чтение — выполнение — вывод».

        ``read_line`` — функция чтения строки с приглашением.
        Возвращает код завершения эмулятора.
        """
        while self.running:
            try:
                line = read_line(self.prompt())
            except EOFError:
                self.write("")
                break
            except KeyboardInterrupt:
                self.write("")
                continue
            self.execute(line)
        return self.last_status
