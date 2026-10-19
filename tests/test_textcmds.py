"""Тесты команд head и uniq."""

import pytest

from sample_tree import TEN_PLUS

NO_FILE = "No such file or directory"


def numbered(count):
    """Вернуть первые ``count`` строк образца ``ten.txt``."""
    return "".join(TEN_PLUS.splitlines(keepends=True)[:count])


def test_head_default_is_ten_lines(run):
    """Без параметров выводятся первые 10 строк."""
    ok, out, err = run("head ten.txt")
    assert ok and not err
    assert out == numbered(10)


@pytest.mark.parametrize("line", ["head -n 3 ten.txt", "head -n3 ten.txt",
                                  "head ten.txt -n 3"])
def test_head_lines_forms(run, line):
    """Число строк: отдельным словом, слитно, после имени файла."""
    assert run(line)[1] == numbered(3)


def test_head_zero_and_large_counts(run):
    """Ноль строк - пустой вывод, много строк - весь файл."""
    assert run("head -n 0 ten.txt") == (True, "", "")
    assert run("head -n 99 ten.txt")[1] == TEN_PLUS


def test_head_bytes(run):
    """``-c`` берёт первые байты, а не строки."""
    assert run("head -c 3 dups.txt")[1] == "a\na\n"
    assert run("head -c 0 dups.txt")[1] == ""


def test_head_several_files_have_headers(run):
    """Для нескольких файлов перед каждым стоит заголовок."""
    _, out, _ = run("head -n 1 dups.txt docs/guide.txt")
    assert out == "==> dups.txt <==\na\n\n==> docs/guide.txt <==\nguide\n"


def test_head_keeps_blank_first_line(run):
    """Пустая первая строка - это вывод (одна пустая строка)."""
    assert run("head -n 1 blank.txt")[1] == "\n"


def test_head_empty_file(run):
    """Пустой файл: успех и пустой вывод."""
    assert run("head empty.txt") == (True, "", "")


def test_head_binary_file_does_not_fail(run):
    """Двоичные данные выводятся без исключений."""
    ok, out, _ = run("head bin.dat")
    assert ok and out == "\x00\x01\n"


def test_head_relative_to_cwd(run):
    """Пути к файлам отсчитываются от текущей папки."""
    run("cd docs")
    assert run("head guide.txt")[1] == "guide\n"
    assert run("head ../dups.txt -n 1")[1] == "a\n"


@pytest.mark.parametrize("line, text", [
    ("head", "head: missing file operand\n"),
    ("head nope", f"head: cannot open 'nope' for reading: {NO_FILE}\n"),
    ("head docs", "head: error reading 'docs': Is a directory\n"),
    ("head -n abc ten.txt", "head: invalid number of lines: 'abc'\n"),
    ("head -n -3 ten.txt", "head: invalid number of lines: '-3'\n"),
    ("head -c x ten.txt", "head: invalid number of bytes: 'x'\n"),
    ("head -n 1 -c 1 ten.txt",
     "head: can't combine line and byte counts\n"),
    ("head -n", "head: option requires an argument -- 'n'\n"),
    ("head -z ten.txt", "head: invalid option -- 'z'\n"),
])
def test_head_errors(run, line, text):
    """Ошибки аргументов и файлов: сообщение в stderr, вывода нет."""
    ok, out, err = run(line)
    assert (ok, out, err) == (False, "", text)


def test_head_reports_each_bad_file(run):
    """Ошибки по каждому файлу, а успешные файлы всё равно выводятся."""
    ok, out, err = run("head -n 1 dups.txt nope docs")
    assert not ok
    assert out == "==> dups.txt <==\na\n"
    assert err == (f"head: cannot open 'nope' for reading: {NO_FILE}\n"
                   "head: error reading 'docs': Is a directory\n")


def test_uniq_collapses_adjacent_only(run):
    """Сравниваются соседние строки: ``a`` в конце остаётся."""
    assert run("uniq dups.txt")[1] == "a\nb\nB\na\n"


def test_uniq_count(run):
    """``-c`` ставит перед строкой число повторов."""
    assert run("uniq -c dups.txt")[1] == (
        "      2 a\n      1 b\n      1 B\n      1 a\n")


def test_uniq_repeated_only(run):
    """``-d`` оставляет только повторяющиеся строки."""
    assert run("uniq -d dups.txt")[1] == "a\n"


def test_uniq_unique_only(run):
    """``-u`` оставляет только неповторяющиеся строки."""
    assert run("uniq -u dups.txt")[1] == "b\nB\na\n"


def test_uniq_repeated_and_unique_is_empty(run):
    """``-d`` вместе с ``-u`` не оставляет ничего."""
    assert run("uniq -d -u dups.txt") == (True, "", "")


def test_uniq_ignore_case(run):
    """``-i`` не различает регистр; берётся первая строка группы."""
    assert run("uniq -i dups.txt")[1] == "a\nb\na\n"
    assert run("uniq -ci dups.txt")[1] == (
        "      2 a\n      2 b\n      1 a\n")


def test_uniq_empty_file(run):
    """Пустой файл: успех и пустой вывод."""
    assert run("uniq empty.txt") == (True, "", "")


def test_uniq_blank_lines_are_lines(run):
    """Пустые строки - тоже строки и тоже схлопываются."""
    assert run("uniq -c blank.txt")[1] == "      1 \n      1 x\n"


@pytest.mark.parametrize("line, text", [
    ("uniq", "uniq: missing file operand\n"),
    ("uniq dups.txt ten.txt", "uniq: extra operand 'ten.txt'\n"),
    ("uniq nope", f"uniq: nope: {NO_FILE}\n"),
    ("uniq docs", "uniq: docs: Is a directory\n"),
    ("uniq -z dups.txt", "uniq: invalid option -- 'z'\n"),
])
def test_uniq_errors(run, line, text):
    """Ошибки аргументов и файлов: сообщение в stderr, вывода нет."""
    ok, out, err = run(line)
    assert (ok, out, err) == (False, "", text)
