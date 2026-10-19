"""Образец VFS для тестов: дерево узлов, собранное в памяти."""

from emulator.vfs import Node

TEN_PLUS = "".join(f"строка {number}\n" for number in range(1, 13))
DUPLICATES = "a\na\nb\nB\na\n"


def file_node(name, text):
    """Создать узел-файл с текстовым содержимым."""
    return Node(name=name, data=text.encode("utf-8"))


def dir_node(name, *children):
    """Создать узел-папку с заданными потомками."""
    return Node(name=name, is_dir=True,
                children={child.name: child for child in children})


def make_tree():
    """Собрать VFS: файлы, скрытый файл, пустая папка и три уровня."""
    return dir_node(
        "root",
        file_node(".hidden", "secret\n"),
        file_node("dups.txt", DUPLICATES),
        file_node("ten.txt", TEN_PLUS),
        file_node("empty.txt", ""),
        file_node("blank.txt", "\nx\n"),
        file_node("bin.dat", "\x00\x01"),
        dir_node("void"),
        dir_node(
            "docs",
            file_node("guide.txt", "guide\n"),
            dir_node("notes", dir_node("2026", file_node("plan.txt", "p\n"))),
        ),
    )
