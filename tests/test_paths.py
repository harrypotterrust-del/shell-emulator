"""Тесты разбора путей и опций команд."""

import pytest

from emulator.errors import CommandError
from emulator.options import parse_options
from emulator.paths import (NOT_A_DIRECTORY, NOT_FOUND, PathError,
                            format_cwd, resolve)
from sample_tree import make_tree

SPEC = {"a": False, "l": False, "n": True}


def names(path, cwd=()):
    """Вернуть имена папок, на которые указывает путь."""
    return resolve(make_tree(), cwd, path).names


def test_relative_path():
    """Относительный путь отсчитывается от текущей папки."""
    assert names("notes/2026", cwd=("docs",)) == ("docs", "notes", "2026")


@pytest.mark.parametrize("path", ["/docs", "~/docs", "~/./docs/"])
def test_absolute_and_home_paths(path):
    """Корень VFS одновременно домашняя папка: ``/`` и ``~`` равны."""
    assert names(path, cwd=("void",)) == ("docs",)


def test_home_and_root_alone():
    """``~`` и ``/`` ведут в корень."""
    assert names("~", cwd=("docs",)) == ()
    assert names("/", cwd=("docs",)) == ()


def test_parent_and_current():
    """``..`` поднимается на уровень, ``.`` остаётся на месте."""
    assert names("../.", cwd=("docs", "notes")) == ("docs",)


def test_parent_of_root_is_root():
    """Выше корня подняться нельзя."""
    assert names("../../..") == ()


def test_location_has_parent():
    """Место содержит родителя; у корня родитель - он сам."""
    root = make_tree()
    assert resolve(root, (), "docs").parent is root
    assert resolve(root, (), ".").parent is root


@pytest.mark.parametrize("path, reason", [
    ("nope", NOT_FOUND),
    ("docs/nope/x", NOT_FOUND),
    ("ten.txt/x", NOT_A_DIRECTORY),
    ("ten.txt/", NOT_A_DIRECTORY),
    ("ten.txt/..", NOT_A_DIRECTORY),
    ("~user", NOT_FOUND),
])
def test_bad_paths(path, reason):
    """Несуществующий путь и путь «через файл» - разные причины."""
    with pytest.raises(PathError, match=reason):
        names(path)


def test_format_cwd():
    """В приглашении корень - ``~``, глубже - ``~/a/b``."""
    assert format_cwd(()) == "~"
    assert format_cwd(("docs", "notes")) == "~/docs/notes"


def test_options_clusters_and_values():
    """Слитные опции и параметры в обеих формах записи."""
    flags, operands = parse_options(["-al", "x"], SPEC)
    assert flags == {"a": True, "l": True}
    assert operands == ["x"]
    assert parse_options(["-n5"], SPEC)[0] == {"n": "5"}
    assert parse_options(["-n", "5", "f"], SPEC) == ({"n": "5"}, ["f"])


def test_options_after_operands_and_double_dash():
    """Опции допустимы после операндов; ``--`` отключает их разбор."""
    assert parse_options(["f", "-a"], SPEC) == ({"a": True}, ["f"])
    assert parse_options(["--", "-a"], SPEC) == ({}, ["-a"])
    assert parse_options(["-"], SPEC) == ({}, ["-"])


@pytest.mark.parametrize("args, text", [
    (["-z"], "invalid option -- 'z'"),
    (["--all"], "unrecognized option '--all'"),
    (["-n"], "option requires an argument -- 'n'"),
])
def test_option_errors(args, text):
    """Неизвестная опция и опция без параметра - ошибка."""
    with pytest.raises(CommandError, match=text):
        parse_options(args, SPEC)
