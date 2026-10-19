"""Тесты команд ls и cd."""

import io

import pytest

from emulator.shell import EXIT_FAILURE, Shell
from sample_tree import TEN_PLUS

ROOT_NAMES = ["bin.dat", "blank.txt", "docs", "dups.txt", "empty.txt",
              "ten.txt", "void"]
TEN_SIZE = len(TEN_PLUS.encode("utf-8"))
MISSING = "ls: cannot access 'nope': No such file or directory\n"


def lines(text):
    """Разбить вывод на строки."""
    return text.splitlines()


def test_ls_hides_dotfiles(run):
    """Без ``-a`` скрытые записи не показываются."""
    ok, out, err = run("ls")
    assert ok and not err
    assert lines(out) == ROOT_NAMES


def test_ls_all_shows_hidden_and_dots(run):
    """С ``-a`` добавляются ``.``, ``..`` и скрытые файлы."""
    _, out, _ = run("ls -a")
    assert lines(out) == [".", "..", ".hidden"] + ROOT_NAMES


def test_ls_long_format(run):
    """С ``-l`` выводятся тип, размер и имя; размеры выровнены."""
    _, out, _ = run("ls -l")
    width = len(str(TEN_SIZE))
    assert lines(out)[0] == f"- {2:>{width}} bin.dat"
    assert f"d {0:>{width}} docs" in lines(out)
    assert f"- {TEN_SIZE} ten.txt" in lines(out)


def test_ls_combined_flags(run):
    """Флаги можно писать слитно: ``-la`` равно ``-l -a``."""
    assert run("ls -la")[1] == run("ls -l -a")[1]


def test_ls_path_argument(run):
    """Путь к папке: выводится её содержимое."""
    assert lines(run("ls docs/notes")[1]) == ["2026"]
    assert lines(run("ls /docs")[1]) == ["guide.txt", "notes"]
    assert lines(run("ls ~/docs/..")[1]) == ROOT_NAMES


def test_ls_file_argument(run):
    """Путь к файлу: выводится сам путь (с ``-l`` - со сведениями)."""
    assert run("ls docs/guide.txt")[1] == "docs/guide.txt\n"
    assert run("ls -l docs/guide.txt")[1] == "- 6 docs/guide.txt\n"


def test_ls_recursive(run):
    """С ``-R`` выводятся все вложенные папки с заголовками."""
    _, out, _ = run("ls -R docs")
    assert out == ("docs:\nguide.txt\nnotes\n\n"
                   "docs/notes:\n2026\n\n"
                   "docs/notes/2026:\nplan.txt\n")


def test_ls_recursive_from_current(run):
    """``ls -R`` без пути начинает с заголовка ``.:``."""
    out = run("ls -R")[1]
    assert out.startswith(".:\n")
    assert "./docs/notes/2026:\nplan.txt" in out


def test_ls_several_paths_get_titles(run):
    """Несколько путей: файлы идут первыми, у папок - заголовки."""
    _, out, _ = run("ls void docs ten.txt")
    assert out == "ten.txt\n\ndocs:\nguide.txt\nnotes\n\nvoid:\n"


def test_ls_empty_directory_prints_nothing(run):
    """Пустая папка: успех и пустой вывод."""
    assert run("ls void") == (True, "", "")


def test_ls_in_current_directory(run):
    """Без пути ``ls`` показывает текущую папку."""
    run("cd docs")
    assert lines(run("ls")[1]) == ["guide.txt", "notes"]


def test_ls_missing_path(run, shell):
    """Несуществующий путь: ошибка и код 1."""
    ok, out, err = run("ls nope")
    assert (ok, out, err) == (False, "", MISSING)
    assert shell.last_status == EXIT_FAILURE


def test_ls_through_file(run):
    """Путь «через файл» - ошибка ``Not a directory``."""
    err = run("ls ten.txt/x")[2]
    assert err == "ls: cannot access 'ten.txt/x': Not a directory\n"


def test_ls_keeps_output_when_one_path_fails(run):
    """Ошибка одного пути не отменяет вывод остальных."""
    ok, out, err = run("ls nope docs")
    assert not ok
    assert out == "docs:\nguide.txt\nnotes\n"
    assert err == MISSING


@pytest.mark.parametrize("line, text", [
    ("ls -z", "ls: invalid option -- 'z'\n"),
    ("ls --all", "ls: unrecognized option '--all'\n"),
])
def test_ls_bad_options(run, line, text):
    """Неизвестные опции - ошибка."""
    assert run(line)[1:] == ("", text)


def test_cd_changes_prompt(run, shell):
    """После ``cd`` приглашение показывает путь от корня."""
    run("cd docs/notes/2026")
    assert shell.prompt().endswith(":~/docs/notes/2026$ ")
    assert lines(run("ls")[1]) == ["plan.txt"]


def test_cd_parent_and_home(run, shell):
    """``cd ..`` поднимается на уровень, ``cd`` без аргументов - в корень."""
    run("cd docs/notes")
    run("cd ..")
    assert shell.cwd == ("docs",)
    run("cd")
    assert shell.cwd == ()


@pytest.mark.parametrize("target", ["/docs", "~/docs", "~/docs/notes/.."])
def test_cd_absolute_forms(run, shell, target):
    """Абсолютные пути и ``~`` работают из любой папки."""
    run("cd void")
    assert run(f"cd {target}")[0]
    assert shell.cwd == ("docs",)


def test_cd_does_not_print(run):
    """Успешный ``cd`` ничего не выводит."""
    assert run("cd docs") == (True, "", "")


def test_cd_dash_returns_to_previous(run, shell):
    """``cd -`` возвращает в прошлую папку и печатает её путь."""
    run("cd docs/notes")
    run("cd /")
    ok, out, _ = run("cd -")
    assert ok and out == "~/docs/notes\n"
    assert shell.cwd == ("docs", "notes")


def test_cd_dash_without_history(run):
    """``cd -`` до первого перехода - ошибка."""
    assert run("cd -")[1:] == ("", "cd: OLDPWD not set\n")


@pytest.mark.parametrize("line, text", [
    ("cd nope", "cd: nope: No such file or directory\n"),
    ("cd ten.txt", "cd: ten.txt: Not a directory\n"),
    ("cd docs void", "cd: too many arguments\n"),
    ("cd -x", "cd: invalid option -- 'x'\n"),
])
def test_cd_errors(run, shell, line, text):
    """Ошибки ``cd`` не меняют текущую папку."""
    ok, out, err = run(line)
    assert (ok, out, err) == (False, "", text)
    assert shell.cwd == ()


def test_double_dash_allows_dash_name(run):
    """После ``--`` аргумент не считается опцией."""
    assert run("cd -- -x")[2] == "cd: -x: No such file or directory\n"


def test_commands_work_without_vfs():
    """Без VFS файловая система пуста, но команды работают."""
    shell = Shell(env={}, out=io.StringIO(), err=io.StringIO())
    assert shell.execute("ls -a")
    assert shell.out.getvalue() == ".\n..\n"
    assert not shell.execute("cd docs")
    assert shell.err.getvalue() == "cd: docs: No such file or directory\n"
