"""Тесты выполнения стартового скрипта."""

import io

from emulator.script import run_script
from emulator.shell import Shell

ENV = {"HOME": "/Users/test"}
MISSING = "нет такого файла.txt"


def make_shell():
    """Создать оболочку с перехватом вывода."""
    return Shell(env=dict(ENV), out=io.StringIO(), err=io.StringIO())


def write_script(tmp_path, text):
    """Записать текст стартового скрипта и вернуть путь к нему."""
    path = tmp_path / "start.txt"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_input_and_output_are_shown(tmp_path):
    """Скрипт показывает и ввод с приглашением, и вывод команды."""
    shell = make_shell()
    assert run_script(shell, write_script(tmp_path, "ls a\n"))
    assert shell.out.getvalue() == (
        f"{shell.prompt()}ls a\n"
        "ls: args=['a']\n"
    )


def test_error_line_is_skipped(tmp_path):
    """Ошибочная строка пропускается, следующие выполняются."""
    shell = make_shell()
    path = write_script(tmp_path, "foo\nls после\n")
    run_script(shell, path)
    assert "ls: args=['после']" in shell.out.getvalue()
    assert f"{path}:1: строка пропущена" in shell.err.getvalue()


def test_skip_notice_uses_real_line_number(tmp_path):
    """Номер в сообщении — настоящий номер строки файла."""
    shell = make_shell()
    path = write_script(tmp_path, "# комментарий\n\nls ok\ncd a b\n")
    run_script(shell, path)
    assert f"{path}:4: строка пропущена" in shell.err.getvalue()


def test_comments_and_blank_lines_are_quiet(tmp_path):
    """Комментарии и пустые строки не выводятся как ввод."""
    shell = make_shell()
    run_script(shell, write_script(tmp_path, "# заголовок\n\n"))
    assert shell.out.getvalue() == ""
    assert shell.err.getvalue() == ""


def test_exit_stops_script(tmp_path):
    """Команда exit прерывает скрипт: строки после неё пропускаются."""
    shell = make_shell()
    path = write_script(tmp_path, "ls до\nexit 0\nls после\n")
    run_script(shell, path)
    assert "ls: args=['до']" in shell.out.getvalue()
    assert "после" not in shell.out.getvalue()
    assert not shell.running


def test_missing_file_reports_error(tmp_path):
    """Несуществующий скрипт — сообщение об ошибке без исключения."""
    shell = make_shell()
    assert not run_script(shell, str(tmp_path / MISSING))
    assert MISSING in shell.err.getvalue()
