"""Разбор командной строки с раскрытием переменных окружения.

Поддерживается подмножество синтаксиса POSIX shell:

* разделение на слова по пробельным символам;
* одинарные кавычки — текст берётся буквально, без раскрытия;
* двойные кавычки — пробелы сохраняются, переменные раскрываются;
* обратный слэш экранирует следующий символ;
* переменные ``$NAME`` и ``${NAME}``; неизвестная переменная
  раскрывается в пустую строку, как в bash.
"""

NOT_FOUND = -1
SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
ESCAPE = "\\"
DOLLAR = "$"
ESCAPABLE_IN_DOUBLE = (DOUBLE_QUOTE, ESCAPE, DOLLAR)


class ParseError(Exception):
    """Ошибка синтаксиса командной строки."""


def is_name_start(char):
    """Проверить, может ли символ начинать имя переменной."""
    return char.isalpha() or char == "_"


def is_name_char(char):
    """Проверить, может ли символ входить в имя переменной."""
    return char.isalnum() or char == "_"


class Tokenizer:
    """Посимвольный разборщик одной строки ввода."""

    def __init__(self, line, env):
        """Подготовить разбор строки ``line`` с окружением ``env``."""
        self.line = line
        self.env = env
        self.pos = 0
        self.tokens = []
        self.current = []
        self.in_token = False

    def run(self):
        """Разобрать строку целиком и вернуть список слов."""
        while self.pos < len(self.line):
            self.consume(self.line[self.pos])
        self.flush()
        return self.tokens

    def consume(self, char):
        """Обработать символ вне кавычек."""
        if char.isspace():
            self.flush()
            self.pos += 1
        elif char == SINGLE_QUOTE:
            self.read_single_quoted()
        elif char == DOUBLE_QUOTE:
            self.read_double_quoted()
        elif char == DOLLAR:
            self.read_variable()
        elif char == ESCAPE:
            self.read_escaped()
        else:
            self.append(char)
            self.pos += 1

    def append(self, text):
        """Добавить текст к текущему слову."""
        self.current.append(text)
        self.in_token = True

    def flush(self):
        """Завершить текущее слово, если оно начато."""
        if self.in_token:
            self.tokens.append("".join(self.current))
        self.current = []
        self.in_token = False

    def read_single_quoted(self):
        """Прочитать текст в одинарных кавычках без раскрытия."""
        end = self.line.find(SINGLE_QUOTE, self.pos + 1)
        if end == NOT_FOUND:
            raise ParseError("unexpected EOF while looking for matching `''")
        self.append(self.line[self.pos + 1:end])
        self.pos = end + 1

    def read_double_quoted(self):
        """Прочитать текст в двойных кавычках с раскрытием переменных."""
        self.in_token = True
        self.pos += 1
        while self.pos < len(self.line):
            char = self.line[self.pos]
            if char == DOUBLE_QUOTE:
                self.pos += 1
                return
            if char == DOLLAR:
                self.read_variable()
            elif char == ESCAPE and self.peek() in ESCAPABLE_IN_DOUBLE:
                self.append(self.peek())
                self.pos += 2
            else:
                self.append(char)
                self.pos += 1
        raise ParseError("unexpected EOF while looking for matching `\"'")

    def read_escaped(self):
        """Прочитать символ, экранированный обратным слэшем."""
        if self.pos + 1 >= len(self.line):
            raise ParseError("unexpected EOF after `\\'")
        self.append(self.line[self.pos + 1])
        self.pos += 2

    def peek(self):
        """Вернуть символ после текущего или пустую строку."""
        nxt = self.pos + 1
        return self.line[nxt] if nxt < len(self.line) else ""

    def read_variable(self):
        """Раскрыть ``$NAME`` или ``${NAME}``; одиночный ``$`` — литерал."""
        nxt = self.peek()
        if nxt == "{":
            name = self.read_braced_name()
        elif is_name_start(nxt):
            name = self.read_plain_name()
        else:
            self.append(DOLLAR)
            self.pos += 1
            return
        value = self.env.get(name, "")
        if value:
            self.append(value)

    def read_braced_name(self):
        """Прочитать имя вида ``${NAME}`` и сдвинуть позицию за ``}``."""
        end = self.line.find("}", self.pos + 2)
        if end == NOT_FOUND:
            raise ParseError("unexpected EOF while looking for matching `}'")
        name = self.line[self.pos + 2:end]
        if not name or not is_name_start(name[0]) or not all(
                is_name_char(char) for char in name):
            raise ParseError(f"${{{name}}}: bad substitution")
        self.pos = end + 1
        return name

    def read_plain_name(self):
        """Прочитать имя вида ``$NAME`` и сдвинуть позицию за него."""
        start = self.pos + 1
        end = start
        while end < len(self.line) and is_name_char(self.line[end]):
            end += 1
        self.pos = end
        return self.line[start:end]


def parse(line, env):
    """Разбить строку на слова, раскрыв переменные из ``env``.

    Возвращает список слов; первое слово — имя команды.
    При синтаксической ошибке возбуждает ``ParseError``.
    """
    return Tokenizer(line, env).run()
