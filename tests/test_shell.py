"""Тесты оболочки: приглашение, команды и цикл REPL."""

import io

from emulator.shell import (EXIT_FAILURE, EXIT_NOT_FOUND, EXIT_SUCCESS,
                            Shell)

ENV = {"HOME": "/Users/test"}
CUSTOM_CODE = 3


def make_shell():
    """Создать оболочку с перехватом вывода."""
    return Shell(env=dict(ENV), out=io.StringIO(), err=io.StringIO())


def test_prompt_format():
    """Приглашение строится из имени пользователя и компьютера."""
    shell = make_shell()
    assert shell.prompt() == f"{shell.user}@{shell.host}:~$ "


def test_stub_prints_name_and_args():
    """Заглушка выводит имя и аргументы с раскрытыми переменными."""
    shell = make_shell()
    assert shell.execute("ls -l $HOME")
    assert shell.out.getvalue() == "ls: args=['-l', '/Users/test']\n"


def test_unknown_command():
    """Неизвестная команда — ошибка с кодом 127."""
    shell = make_shell()
    assert not shell.execute("foo bar")
    assert shell.err.getvalue() == "foo: command not found\n"
    assert shell.last_status == EXIT_NOT_FOUND


def test_cd_too_many_args():
    """Для cd больше одного аргумента — ошибка."""
    shell = make_shell()
    assert not shell.execute("cd a b")
    assert shell.err.getvalue() == "cd: too many arguments\n"
    assert shell.last_status == EXIT_FAILURE


def test_syntax_error():
    """Незакрытая кавычка — синтаксическая ошибка."""
    shell = make_shell()
    assert not shell.execute("ls 'abc")
    assert shell.err.getvalue().startswith("syntax error")


def test_exit_with_code():
    """Команда exit останавливает оболочку с заданным кодом."""
    shell = make_shell()
    assert shell.execute(f"exit {CUSTOM_CODE}")
    assert not shell.running
    assert shell.last_status == CUSTOM_CODE


def test_exit_bad_argument():
    """Нечисловой аргумент exit — ошибка, оболочка продолжает работу."""
    shell = make_shell()
    assert not shell.execute("exit abc")
    assert shell.running


def test_repl_runs_until_exit():
    """REPL выполняет команды по очереди до exit."""
    lines = iter(["ls a", "nope", f"exit {CUSTOM_CODE}", "ls never"])
    shell = make_shell()
    assert shell.run_repl(lambda prompt: next(lines)) == CUSTOM_CODE
    assert shell.out.getvalue() == "ls: args=['a']\n"
    assert shell.err.getvalue() == "nope: command not found\n"


def test_repl_stops_on_eof():
    """Ctrl+D (конец ввода) завершает REPL."""
    def read_eof(prompt):
        """Имитировать конец ввода."""
        raise EOFError

    assert make_shell().run_repl(read_eof) == EXIT_SUCCESS
