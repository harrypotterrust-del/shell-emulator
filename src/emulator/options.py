"""Разбор коротких опций команд: ``-l``, ``-la``, ``-n 5``, ``--``."""

from emulator.errors import CommandError

DASH = "-"
LONG_PREFIX = "--"
END_OF_OPTIONS = "--"


def is_option(arg):
    """Проверить, что аргумент - опция (одиночный ``-`` - операнд)."""
    return arg.startswith(DASH) and arg != DASH


def read_cluster(arg, spec, rest, options):
    """Разобрать слово вида ``-abc`` и записать опции в ``options``.

    Опции с параметром забирают остаток слова (``-n5``) или следующее
    слово из ``rest`` (``-n 5``).
    """
    if arg.startswith(LONG_PREFIX):
        raise CommandError(f"unrecognized option '{arg}'")
    letters = arg[1:]
    for index, letter in enumerate(letters):
        if letter not in spec:
            raise CommandError(f"invalid option -- '{letter}'")
        if not spec[letter]:
            options[letter] = True
            continue
        value = letters[index + 1:]
        if not value and not rest:
            raise CommandError(f"option requires an argument -- '{letter}'")
        options[letter] = value or rest.pop(0)
        return


def parse_options(args, spec):
    """Разделить аргументы команды на опции и операнды.

    ``spec`` - словарь «буква опции -> нужен ли ей параметр».
    Возвращает пару (опции, операнды): опции - словарь «буква ->
    значение» (``True`` для опций без параметра). Опции можно ставить
    после операндов; всё после ``--`` считается операндами.
    """
    options, operands = {}, []
    rest = list(args)
    while rest:
        arg = rest.pop(0)
        if arg == END_OF_OPTIONS:
            operands.extend(rest)
            break
        if is_option(arg):
            read_cluster(arg, spec, rest, options)
        else:
            operands.append(arg)
    return options, operands
