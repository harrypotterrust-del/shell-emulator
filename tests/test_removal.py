"""Тесты команды rm: удаление только в памяти, режимы и защита."""

import io
import os

import pytest

from emulator.shell import Shell
from emulator.vfs import load_vfs

IS_DIR = "rm: cannot remove 'docs': Is a directory\n"
CWD_REFUSAL = "it is or contains the current directory"


def names(run, line="ls -a"):
    """Выполнить ``ls`` и вернуть имена из его вывода."""
    return run(line)[1].splitlines()


def test_rm_removes_file(run):
    """Файл удаляется молча и пропадает из ``ls``."""
    assert run("rm ten.txt") == (True, "", "")
    assert "ten.txt" not in names(run, "ls")
    assert not run("head ten.txt")[0]


def test_rm_removes_several_files(run):
    """Можно указать несколько файлов сразу."""
    assert run("rm dups.txt empty.txt .hidden")[0]
    assert names(run) == [".", "..", "bin.dat", "blank.txt", "docs",
                          "ten.txt", "void"]


def test_rm_relative_and_absolute_paths(run):
    """Пути отсчитываются от текущей папки; ``/`` и ``~`` - от корня."""
    run("cd docs")
    assert run("rm guide.txt ../ten.txt ~/dups.txt /empty.txt")[0]
    assert names(run, "ls") == ["notes"]
    assert "ten.txt" not in names(run, "ls ..")


def test_rm_directory_needs_flag(run, shell):
    """Папка без ``-r`` и ``-d`` не удаляется."""
    ok, out, err = run("rm docs")
    assert (ok, out, err) == (False, "", IS_DIR)
    assert "docs" in shell.root.children


def test_rm_d_removes_empty_directory_only(run):
    """``-d`` удаляет пустую папку, но не удаляет папку с файлами."""
    assert run("rm -d void") == (True, "", "")
    assert "void" not in names(run, "ls")
    assert run("rm -d docs")[2] == (
        "rm: cannot remove 'docs': Directory not empty\n")


@pytest.mark.parametrize("flag", ["-r", "-R", "-rf", "-fr"])
def test_rm_recursive(run, flag):
    """``-r`` (и ``-R``) удаляет папку со всем содержимым."""
    assert run(f"rm {flag} docs") == (True, "", "")
    assert "docs" not in names(run, "ls")
    assert not run("ls docs/notes")[0]


def test_rm_verbose_file_and_tree(run):
    """``-v`` печатает удаления; вложенное идёт раньше папки."""
    assert run("rm -v ten.txt")[1] == "removed 'ten.txt'\n"
    assert run("rm -rv docs")[1] == (
        "removed 'docs/guide.txt'\n"
        "removed 'docs/notes/2026/plan.txt'\n"
        "removed directory 'docs/notes/2026'\n"
        "removed directory 'docs/notes'\n"
        "removed directory 'docs'\n")


def test_rm_verbose_empty_directory(run):
    """``-d -v`` сообщает об удалении пустой папки."""
    assert run("rm -dv void/")[1] == "removed directory 'void'\n"


def test_rm_force_ignores_missing(run):
    """``-f``: отсутствующий путь - не ошибка, остальные удаляются."""
    assert run("rm -f nope ten.txt") == (True, "", "")
    assert "ten.txt" not in names(run, "ls")
    assert run("rm -f ten.txt/x") == (True, "", "")


def test_rm_force_without_operands(run):
    """``rm -f`` без операндов молча успешен."""
    assert run("rm -f") == (True, "", "")


def test_rm_force_does_not_remove_directories(run):
    """``-f`` не заменяет ``-r``: папка всё равно требует флага."""
    assert run("rm -f docs")[2] == IS_DIR


def test_rm_missing_operand(run):
    """Без операндов (и без ``-f``) - ошибка."""
    assert run("rm") == (False, "", "rm: missing operand\n")
    assert run("rm -r")[2] == "rm: missing operand\n"


@pytest.mark.parametrize("line, text", [
    ("rm nope", "rm: cannot remove 'nope': No such file or directory\n"),
    ("rm ten.txt/x", "rm: cannot remove 'ten.txt/x': Not a directory\n"),
    ("rm -z ten.txt", "rm: invalid option -- 'z'\n"),
    ("rm --force ten.txt", "rm: unrecognized option '--force'\n"),
])
def test_rm_errors(run, shell, line, text):
    """Ошибки путей и опций: сообщение в stderr, ничего не удалено."""
    ok, out, err = run(line)
    assert (ok, out, err) == (False, "", text)
    assert "ten.txt" in shell.root.children


@pytest.mark.parametrize("operand", [".", "..", "docs/.", "docs/..",
                                     "docs/notes/.."])
def test_rm_refuses_dot_names(run, operand):
    """``.`` и ``..`` удалять нельзя ни в каком виде."""
    ok, out, err = run(f"rm -r {operand}")
    assert (ok, out) == (False, "")
    assert err == ("rm: refusing to remove '.' or '..' directory: "
                   f"skipping '{operand}'\n")


@pytest.mark.parametrize("operand", ["/", "~", "docs/.."])
def test_rm_refuses_root(run, shell, operand):
    """Корень VFS не удаляется."""
    assert not run(f"rm -rf {operand}")[0]
    assert "docs" in shell.root.children


def test_rm_refuses_current_directory_and_parents(run, shell):
    """Текущая папка и её родители не удаляются, даже с ``-rf``."""
    run("cd docs/notes")
    for operand in ["~/docs/notes", "/docs", "../../docs"]:
        ok, out, err = run(f"rm -rf {operand}")
        assert (ok, out) == (False, "")
        assert CWD_REFUSAL in err
    assert "docs" in shell.root.children
    assert shell.cwd == ("docs", "notes")


def test_rm_allows_sibling_of_current_directory(run):
    """Соседние папки и вложенные в текущую удалять можно."""
    run("cd docs")
    assert run("rm -r notes ../void")[0]
    assert names(run, "ls") == ["guide.txt"]


def test_rm_keeps_going_after_error(run):
    """Ошибка одного операнда не отменяет удаление остальных."""
    ok, out, err = run("rm -v nope ten.txt docs dups.txt")
    assert not ok
    assert out == "removed 'ten.txt'\nremoved 'dups.txt'\n"
    assert err == ("rm: cannot remove 'nope': No such file or directory\n"
                   f"{IS_DIR}")


def test_rm_second_operand_inside_removed_one(run):
    """Путь внутри уже удалённой папки к этому моменту не существует."""
    ok, _, err = run("rm -r docs docs/guide.txt")
    assert not ok
    assert err == ("rm: cannot remove 'docs/guide.txt': "
                   "No such file or directory\n")


def test_rm_updates_vfs_tree(run):
    """Служебная команда ``vfs-tree`` показывает уже изменённую VFS."""
    run("rm -r docs")
    tree = run("vfs-tree")[1]
    assert "docs" not in tree
    assert "ten.txt" in tree


def test_cd_dash_to_removed_directory(run, shell):
    """``cd -`` в удалённую папку - ошибка, а не падение."""
    run("cd docs")
    run("cd /")
    run("rm -r docs")
    ok, out, err = run("cd -")
    assert (ok, out) == (False, "")
    assert err == "cd: ~/docs: No such file or directory\n"
    assert shell.cwd == ()


def test_rm_without_vfs():
    """Без VFS удалять нечего: путь не найден, ``-f`` молчит."""
    shell = Shell(env={}, out=io.StringIO(), err=io.StringIO())
    assert not shell.execute("rm file.txt")
    assert shell.err.getvalue() == (
        "rm: cannot remove 'file.txt': No such file or directory\n")
    assert shell.execute("rm -f file.txt")


def test_disk_is_not_modified(tmp_path):
    """Удаление в эмуляторе не трогает исходную директорию на диске."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    before = sorted(os.walk(tmp_path))
    shell = Shell(env={}, out=io.StringIO(), err=io.StringIO(),
                  vfs=load_vfs(str(tmp_path)))
    assert shell.execute("rm -r docs b.txt")
    assert "docs" not in shell.root.children
    assert sorted(os.walk(tmp_path)) == before
    assert (tmp_path / "docs" / "a.txt").read_text() == "a"
