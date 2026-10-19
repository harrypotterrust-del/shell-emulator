"""Оболочка эмулятора: приглашение, выполнение команд и цикл REPL."""

import getpass
import os
import socket
import sys

from emulator.commands import COMMANDS
from emulator.errors import CommandError, ExitRequest
from emulator.parser import ParseError, parse
from emulator.paths import format_cwd
from emulator.vfs import Node

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_NOT_FOUND = 127


def short_hostname():
    """Вернуть имя компьютера без доменной части (``.local``)."""
    return socket.gethostname().split(".")[0]


class Shell:
    """Эмулятор командной оболочки UNIX-подобной ОС."""

    def __init__(self, env=None, out=None, err=None, config=None,
                 vfs=None):
        """Создать оболочку.

        ``env`` - переменные окружения (по умолчанию - реальные из ОС),
        ``out`` и ``err`` - потоки для вывода и сообщений об ошибках,
        ``config`` - параметры запуска эмулятора,
        ``vfs`` - корневой узел виртуальной файловой системы; пока она
        не загружена, команды работают с пустым корнем.
        """
        self.env = dict(os.environ) if env is None else env
        self.config = config
        self.vfs = vfs
        self.blank = Node(name="", is_dir=True)
        self.out = out if out is not None else sys.stdout
        self.err = err if err is not None else sys.stderr
        self.user = getpass.getuser()
        self.host = short_hostname()
        self.cwd = ()
        self.oldpwd = None
        self.running = True
        self.last_status = EXIT_SUCCESS

    @property
    def root(self):
        """Корень файловой системы: загруженная VFS или пустая папка."""
        return self.vfs if self.vfs is not None else self.blank

    def prompt(self):
        """Сформировать приглашение вида ``user@host:~/docs$``."""
        return f"{self.user}@{self.host}:{format_cwd(self.cwd)}$ "

    def change_dir(self, names):
        """Сделать текущей папку ``names``, запомнив прежнюю (``cd -``)."""
        self.oldpwd = self.cwd
        self.cwd = tuple(names)

    def write(self, text):
        """Вывести текст команды в стандартный вывод."""
        print(text, file=self.out, flush=True)

    def error(self, message):
        """Вывести сообщение об ошибке в поток ошибок."""
        print(message, file=self.err, flush=True)

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
            if exc.output is not None:
                self.write(exc.output)
            lines = str(exc).splitlines()
            return self.fail("\n".join(f"{name}: {line}" for line in lines),
                             EXIT_FAILURE)
        except ExitRequest as exc:
            self.running = False
            self.last_status = exc.code
            return True
        if output is not None:
            self.write(output)
        self.last_status = EXIT_SUCCESS
        return True

    def fail(self, message, status):
        """Сообщить об ошибке, запомнить код и вернуть ``False``."""
        self.error(message)
        self.last_status = status
        return False

    def run_repl(self, read_line=input):
        """Запустить интерактивный цикл «чтение - выполнение - вывод».

        ``read_line`` - функция чтения строки с приглашением.
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
