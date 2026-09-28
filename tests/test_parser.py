"""Тесты разбора командной строки."""

import pytest

from emulator.parser import ParseError, parse

ENV = {"HOME": "/Users/test", "USER": "test"}
BAD_LINES = ["ls 'abc", 'ls "abc', "ls ${HOME", "ls ${1x}", "ls \\"]


def test_split_by_spaces():
    """Слова разделяются любым количеством пробелов."""
    assert parse("ls   -l  /tmp", ENV) == ["ls", "-l", "/tmp"]


def test_expand_variable():
    """Переменная $NAME раскрывается."""
    assert parse("cd $HOME", ENV) == ["cd", "/Users/test"]


def test_expand_braced_variable():
    """Переменная ${NAME} раскрывается внутри слова."""
    assert parse("ls ${HOME}/docs", ENV) == ["ls", "/Users/test/docs"]


def test_unknown_variable_is_empty():
    """Неизвестная переменная без кавычек исчезает, как в bash."""
    assert parse("ls $NOPE", ENV) == ["ls"]


def test_single_quotes_keep_text():
    """В одинарных кавычках переменные не раскрываются."""
    assert parse("ls '$HOME dir'", ENV) == ["ls", "$HOME dir"]


def test_double_quotes_expand():
    """В двойных кавычках пробелы сохраняются, переменные раскрываются."""
    assert parse('ls "$USER files"', ENV) == ["ls", "test files"]


def test_empty_quotes_give_empty_word():
    """Пустые кавычки дают пустой аргумент."""
    assert parse('cd ""', ENV) == ["cd", ""]


def test_escape():
    """Обратный слэш экранирует пробел и знак доллара."""
    assert parse(r"ls my\ dir \$HOME", ENV) == ["ls", "my dir", "$HOME"]


def test_lone_dollar():
    """Одиночный знак доллара остаётся как есть."""
    assert parse("ls $ 5$", ENV) == ["ls", "$", "5$"]


def test_empty_line():
    """Пустая строка даёт пустой список слов."""
    assert parse("   ", ENV) == []


@pytest.mark.parametrize("line", BAD_LINES)
def test_syntax_errors(line):
    """Незакрытые кавычки и неверные подстановки — ошибка разбора."""
    with pytest.raises(ParseError):
        parse(line, ENV)
