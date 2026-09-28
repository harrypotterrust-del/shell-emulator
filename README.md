# Эмулятор командной оболочки (вариант 5)

## Описание

Консольный (CLI) эмулятор командной строки UNIX-подобной ОС на Python.

Этап 1 (REPL) — минимальный прототип:

- приглашение к вводу вида `username@hostname:~$` строится из реальных
  данных ОС (имя пользователя и имя компьютера);
- парсер раскрывает переменные окружения реальной ОС (`$HOME`,
  `${USER}`) и поддерживает кавычки и экранирование;
- сообщения об ошибках: неизвестная команда, неверные аргументы,
  синтаксическая ошибка;
- команды-заглушки `ls`, `cd` и команда `exit`.

## Команды и настройки

| Команда | Описание |
|---|---|
| `ls [аргументы...]` | заглушка: выводит имя команды и аргументы |
| `cd [путь]` | заглушка: выводит имя и аргумент; больше одного аргумента — ошибка |
| `exit [код]` | завершает работу с кодом (по умолчанию 0); код должен быть числом |

Правила разбора строки:

| Запись | Результат |
|---|---|
| `$NAME`, `${NAME}` | значение переменной окружения; неизвестная — пустая строка |
| `'текст'` | текст буквально, без раскрытия переменных |
| `"текст"` | пробелы сохраняются, переменные раскрываются |
| `\символ` | экранирование следующего символа |

Коды завершения: `0` — успех, `1` — ошибка аргументов или синтаксиса,
`127` — команда не найдена.

## Сборка и запуск тестов

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make test     # автотесты pytest
make lint     # проверка стиля flake8
./run.sh      # запуск эмулятора (или make run)
```

## Примеры использования

```text
aleksandr@MacBook-Air:~$ ls -l $HOME
ls: args=['-l', '/Users/aleksandr']
aleksandr@MacBook-Air:~$ cd "my folder"
cd: args=['my folder']
aleksandr@MacBook-Air:~$ ls '$HOME' "${USER} files"
ls: args=['$HOME', 'aleksandr files']
aleksandr@MacBook-Air:~$ cd a b
cd: too many arguments
aleksandr@MacBook-Air:~$ foo
foo: command not found
aleksandr@MacBook-Air:~$ ls "abc
syntax error: unexpected EOF while looking for matching `"'
aleksandr@MacBook-Air:~$ exit abc
exit: abc: numeric argument required
aleksandr@MacBook-Air:~$ exit
```
