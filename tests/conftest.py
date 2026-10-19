"""Общие фикстуры: оболочка с небольшой VFS, собранной в памяти."""

import io

import pytest

from emulator.shell import Shell
from sample_tree import make_tree


@pytest.fixture
def shell():
    """Оболочка с VFS в памяти и перехватом вывода."""
    return Shell(env={"HOME": "/Users/test"}, out=io.StringIO(),
                 err=io.StringIO(), vfs=make_tree())


@pytest.fixture
def run(shell):
    """Выполнить строку и вернуть (успех, вывод, ошибки) только этой строки."""
    def runner(line):
        """Очистить потоки, выполнить ``line`` и собрать результат."""
        for stream in (shell.out, shell.err):
            stream.seek(0)
            stream.truncate()
        ok = shell.execute(line)
        return ok, shell.out.getvalue(), shell.err.getvalue()

    return runner
