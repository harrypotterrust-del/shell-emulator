# Эмулятор командной оболочки (вариант 5)

## Описание

Консольный (CLI) эмулятор командной строки UNIX-подобной ОС на Python.

Этап 1 (REPL) - минимальный прототип:

- приглашение к вводу вида `username@hostname:~$` строится из реальных
  данных ОС (имя пользователя и имя компьютера);
- парсер раскрывает переменные окружения реальной ОС (`$HOME`,
  `${USER}`) и поддерживает кавычки и экранирование;
- сообщения об ошибках: неизвестная команда, неверные аргументы,
  синтаксическая ошибка;
- команды-заглушки `ls`, `cd` и команда `exit`.

Этап 2 (конфигурация) - эмулятор настраивается снаружи:

- параметры командной строки: путь к VFS и путь к стартовому скрипту;
- при запуске выводятся все заданные параметры (отладочный вывод);
- стартовый скрипт выполняется построчно, на экране показывается как
  ввод, так и вывод - имитация диалога с пользователем;
- ошибочная строка пропускается, об этом сообщается с указанием файла
  и номера строки, выполнение продолжается со следующей строки.

Этап 3 (VFS) - подключена виртуальная файловая система:

- источник VFS - директория на диске пользователя, она читается один
  раз при запуске и больше не изменяется;
- всё содержимое, включая двоичные файлы, хранится в памяти в виде
  байтов; распаковка и запись на диск не выполняются;
- об ошибке загрузки сообщается отдельно: путь не существует, вместо
  каталога указан файл, файл слишком велик, вложенность слишком
  глубокая;
- служебная команда `vfs-tree` показывает загруженное дерево;
- после загрузки выводится сводка: число папок, файлов и байт.

Этап 4 (основные команды) - команды работают с VFS в памяти:

- `ls` и `cd` стали настоящими: пути, `.`, `..`, `~`, режимы `-a`,
  `-l`, `-R`, возврат `cd -`; приглашение показывает текущую папку;
- новые команды `head` (начало файла) и `uniq` (повторы подряд);
- ошибки сообщаются в стиле UNIX: нет такого файла, не каталог,
  неверная опция, лишний операнд;
- стартовый скрипт `startup/stage4_all.txt` проверяет все режимы
  команд и все виды ошибок на демонстрационной VFS.

Этап 5 (дополнительные команды) - команда, изменяющая VFS:

- `rm` удаляет файлы и папки (`-r`, `-d`, `-f`, `-v`);
- все изменения делаются только в оперативной памяти: исходная
  директория на диске не затрагивается, после перезапуска эмулятора
  VFS снова полная;
- `rm` отказывается удалять корень, `.` и `..`, а также текущую папку
  и её родителей;
- стартовый скрипт `startup/stage5_all.txt` проверяет все режимы и
  все виды ошибок на VFS `rm_demo`.

## Виртуальная файловая система

| Свойство | Значение |
|---|---|
| Источник | директория, заданная параметром `--vfs` |
| Хранение | дерево узлов `Node` в оперативной памяти |
| Содержимое файлов | байты, двоичные данные не искажаются |
| Предел размера файла | 1 МиБ |
| Предел вложенности | 16 уровней |
| Символические ссылки | пропускаются: могут вести наружу и зацикливаться |

Ошибка загрузки не завершает эмулятор: он сообщает о ней и
продолжает работу без VFS.

Примеры источников VFS в папке `vfs_examples/`:

| Папка | Содержимое |
|---|---|
| `minimal/` | один файл в корне |
| `flat/` | несколько файлов в одной папке, включая двоичный |
| `deep/` | четыре уровня папок и файлов |
| `demo/` | для этапа 4: скрытый файл, повторы в `log.txt`, 12 строк в `numbers.txt`, папки `docs/notes/2026` |
| `rm_demo/` | для этапа 5: файлы, скрытый файл и четыре папки разной глубины, которые удаляются по очереди |

## Параметры командной строки

| Параметр | Описание |
|---|---|
| `--vfs PATH` | путь к физическому расположению VFS |
| `--script PATH` | путь к стартовому скрипту эмулятора |

Оба параметра необязательны. Отладочный вывод при запуске:

```text
=== Параметры эмулятора ===
VFS:    vfs_examples/minimal
Script: startup/stage2_ok.txt
===========================
```

Незаданный параметр показывается как `(не задан)`.

Принятые решения этапа:

- после выполнения стартового скрипта эмулятор переходит в
  интерактивный режим (как `bash --init-file`); если скрипт завершился
  командой `exit`, оставшиеся строки не выполняются и REPL не
  открывается;
- путь к VFS на этом этапе только принимается и выводится - загрузка
  содержимого в память и диагностика ошибок загрузки относятся к
  этапу 3.

## Стартовые скрипты эмулятора

Текстовый файл с командами, по одной на строку. Пустые строки и
строки, начинающиеся с `#`, пропускаются без вывода.

| Файл | Назначение |
|---|---|
| `startup/stage2_ok.txt` | только корректные команды |
| `startup/stage2_errors.txt` | ошибочные строки пропускаются |
| `startup/stage2_exit.txt` | `exit` прерывает выполнение скрипта |
| `startup/stage3_all.txt` | команды этапов 1-3, работа с VFS и все виды ошибок |
| `startup/stage4_all.txt` | все режимы `ls`, `cd`, `head`, `uniq`, работа с VFS и ошибки |
| `startup/stage5_all.txt` | все режимы `rm`, изменение VFS в памяти и ошибки |

## Скрипты реальной ОС

Каждый скрипт в `scripts/` вызывает эмулятор со своим набором
параметров командной строки:

| Скрипт | Параметры |
|---|---|
| `run_default.sh` | без параметров |
| `run_vfs_only.sh` | только `--vfs` |
| `run_script_only.sh` | только `--script` |
| `run_all.sh` | `--vfs` и `--script` |
| `run_exit_script.sh` | скрипт с командой `exit` |
| `run_missing_script.sh` | несуществующий стартовый скрипт |
| `run_vfs_minimal.sh` | минимальная VFS |
| `run_vfs_flat.sh` | несколько файлов в одной папке |
| `run_vfs_deep.sh` | четыре уровня папок и файлов |
| `run_vfs_missing.sh` | ошибка: директории не существует |
| `run_vfs_not_dir.sh` | ошибка: вместо каталога указан файл |
| `run_stage4.sh` | этап 4: VFS `demo` и скрипт `stage4_all.txt` |
| `run_stage5.sh` | этап 5: VFS `rm_demo`, скрипт `stage5_all.txt`, затем список файлов на диске |

## Команды и настройки

| Команда | Описание |
|---|---|
| `ls [-a] [-l] [-R] [путь...]` | содержимое папок и сведения о файлах |
| `cd [путь]` | сменить текущую папку; без пути - в корень, `cd -` - в прошлую |
| `head [-n N \| -c N] файл...` | первые строки (по умолчанию 10) или байты файлов |
| `uniq [-c] [-d] [-u] [-i] файл` | убрать подряд идущие повторы строк |
| `rm [-r] [-f] [-v] [-d] путь...` | удаляет файлы и папки из VFS (только в памяти) |
| `exit [код]` | завершает работу с кодом (по умолчанию 0); код должен быть числом |
| `vfs-tree` | служебная команда: выводит дерево загруженной VFS |

Режимы команд:

| Режим | Что делает |
|---|---|
| `ls -a` | показывает скрытые записи (имя с точки), а также `.` и `..` |
| `ls -l` | тип (`d` - папка, `-` - файл), размер в байтах, имя; у папок размер 0 |
| `ls -R` | рекурсивно обходит подпапки, перед каждой печатает `путь:` |
| `ls путь...` | для файла выводит его путь, для папки - содержимое; если путей несколько, у папок печатаются заголовки |
| `cd -` | возвращает в прошлую папку и печатает её путь |
| `head -n N` | первые `N` строк (`-n3` и `-n 3` равнозначны) |
| `head -c N` | первые `N` байтов; вместе с `-n` использовать нельзя |
| `head файл1 файл2` | перед каждым файлом печатается заголовок `==> имя <==` |
| `uniq -c` | перед строкой печатается число повторов |
| `uniq -d` | только строки, которые повторяются |
| `uniq -u` | только строки, которые не повторяются |
| `uniq -i` | регистр букв не различается |
| `rm путь...` | удаляет файлы; папку без `-r` и `-d` не удаляет (`Is a directory`) |
| `rm -r` (`-R`) | удаляет папку вместе со всем содержимым |
| `rm -d` | удаляет пустую папку; непустую не трогает (`Directory not empty`) |
| `rm -f` | отсутствующий путь не считается ошибкой; `rm -f` без путей успешно ничего не делает |
| `rm -v` | печатает `removed 'путь'` и `removed directory 'путь'`, вложенное раньше папки |

Опции можно записывать слитно (`ls -la`), ставить после операндов
(`head файл -n 2`); после `--` всё считается операндами. Обработка
нескольких операндов продолжается после ошибки одного из них:
успешный вывод печатается, ошибки идут в поток ошибок, код возврата 1.

Пути в VFS:

| Запись | Значение |
|---|---|
| `docs/notes` | от текущей папки |
| `/docs`, `~/docs` | от корня VFS; корень одновременно домашняя папка |
| `.`, `..` | текущая папка, родитель; выше корня подняться нельзя |

Принятые решения этапов 4 и 5:

- вывод `ls` по одному имени в строке (как `ls -1`), порядок по имени;
- прав доступа и дат в VFS нет, поэтому `ls -l` показывает только
  тип и размер;
- `head` и `uniq` без файла не читают стандартный ввод (конвейеров
  в эмуляторе нет), а сообщают `missing file operand`;
- двоичные данные выводятся как текст UTF-8, нечитаемые байты
  заменяются на символ замены;
- если VFS не загружена (параметр не задан или была ошибка загрузки),
  команды работают с пустым корнем: `ls -a` покажет только `.` и `..`;
- сообщения об ошибках команд такие же, как у GNU-утилит
  (`No such file or directory`, `Not a directory`, `Is a directory`);
- `rm` изменяет только дерево в памяти; чтобы вернуть удалённое,
  достаточно перезапустить эмулятор;
- `rm` не удаляет корень VFS, `.` и `..`, а также текущую папку и всех
  её родителей: оболочка осталась бы в несуществующем месте. Это
  правило действует и с `-f`;
- `rm` обрабатывает операнды по очереди: ошибка одного не отменяет
  удаление остальных, `rm -r docs docs/a.txt` сообщит об отсутствии
  второго пути, так как он уже удалён вместе с `docs`;
- запроса подтверждения (`-i`) нет, `-f` лишь молчит об отсутствующих
  путях.

Правила разбора строки:

| Запись | Результат |
|---|---|
| `$NAME`, `${NAME}` | значение переменной окружения; неизвестная - пустая строка |
| `'текст'` | текст буквально, без раскрытия переменных |
| `"текст"` | пробелы сохраняются, переменные раскрываются |
| `\символ` | экранирование следующего символа |

Коды завершения: `0` - успех, `1` - ошибка аргументов или синтаксиса,
`127` - команда не найдена.

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

Интерактивная работа с VFS `vfs_examples/demo` (`./run.sh --vfs
vfs_examples/demo`):

```text
aleksandr@MacBook-Air:~$ ls
docs
log.txt
numbers.txt
aleksandr@MacBook-Air:~$ ls -l
d   0 docs
-  75 log.txt
- 192 numbers.txt
aleksandr@MacBook-Air:~$ cd docs/notes
aleksandr@MacBook-Air:~/docs/notes$ ls -R ..
..:
notes
readme.txt

../notes:
2026
todo.txt

../notes/2026:
plan.txt
aleksandr@MacBook-Air:~/docs/notes$ head -n 1 todo.txt
проверить ls
aleksandr@MacBook-Air:~/docs/notes$ cd -
~
aleksandr@MacBook-Air:~$ uniq -c log.txt
      2 INFO start
      1 INFO ready
      1 warn disk
      1 WARN disk
      1 INFO ready
      1 ERROR fail
aleksandr@MacBook-Air:~$ uniq -di log.txt
INFO start
warn disk
aleksandr@MacBook-Air:~$ head -n 2 log.txt docs/readme.txt
==> log.txt <==
INFO start
INFO start

==> docs/readme.txt <==
Демонстрационная VFS для этапа 4.
```

Ошибки (команда сообщает о них и возвращает код 1, оболочка
продолжает работу):

```text
aleksandr@MacBook-Air:~$ ls missing
ls: cannot access 'missing': No such file or directory
aleksandr@MacBook-Air:~$ cd log.txt
cd: log.txt: Not a directory
aleksandr@MacBook-Air:~$ head docs
head: error reading 'docs': Is a directory
aleksandr@MacBook-Air:~$ head -n abc numbers.txt
head: invalid number of lines: 'abc'
aleksandr@MacBook-Air:~$ uniq log.txt numbers.txt
uniq: extra operand 'numbers.txt'
aleksandr@MacBook-Air:~$ ls -l log.txt missing docs
- 75 log.txt

docs:
d  0 notes
- 58 readme.txt
ls: cannot access 'missing': No such file or directory
aleksandr@MacBook-Air:~$ ls -z
ls: invalid option -- 'z'
aleksandr@MacBook-Air:~$ cd a b
cd: too many arguments
aleksandr@MacBook-Air:~$ foo
foo: command not found
aleksandr@MacBook-Air:~$ ls "abc
syntax error: unexpected EOF while looking for matching `"'
aleksandr@MacBook-Air:~$ ls $HOME
ls: cannot access '/Users/aleksandr': No such file or directory
aleksandr@MacBook-Air:~$ exit abc
exit: abc: numeric argument required
aleksandr@MacBook-Air:~$ exit
```

Последняя пара строк показывает раскрытие переменных: команда
получила уже подставленный путь `$HOME`, которого нет в VFS.

Стартовый скрипт этапа 4 (`./scripts/run_stage4.sh`) выполняет все
режимы команд подряд; многоточие означает пропущенные строки:

```text
=== Параметры эмулятора ===
VFS:    vfs_examples/demo
Script: startup/stage4_all.txt
===========================
VFS загружена: корень 'demo', папок: 3, файлов: 6, байт: 454
aleksandr@MacBook-Air:~$ ls -la docs
d  0 .
d  0 ..
d  0 notes
- 58 readme.txt
...
aleksandr@MacBook-Air:~/docs$ cd notes/2026
aleksandr@MacBook-Air:~/docs/notes/2026$ ls -l
- 26 plan.txt
aleksandr@MacBook-Air:~/docs/notes/2026$ cd ../..
aleksandr@MacBook-Air:~/docs$ cd -
~/docs/notes/2026
...
aleksandr@MacBook-Air:~$ head -c 25 log.txt
INFO start
INFO start
INF
...
aleksandr@MacBook-Air:~$ uniq -ci log.txt
      2 INFO start
      1 INFO ready
      2 warn disk
      1 INFO ready
      1 ERROR fail
...
aleksandr@MacBook-Air:~$ head -n 1 -c 1 numbers.txt
head: can't combine line and byte counts
startup/stage4_all.txt:69: строка пропущена
```

Стартовый скрипт этапа 5 (`./scripts/run_stage5.sh`), фрагменты; после
выхода из эмулятора скрипт печатает список файлов на диске:

```text
=== Параметры эмулятора ===
VFS:    vfs_examples/rm_demo
Script: startup/stage5_all.txt
===========================
VFS загружена: корень 'rm_demo', папок: 6, файлов: 9, байт: 251
aleksandr@MacBook-Air:~$ rm old.txt
aleksandr@MacBook-Air:~$ rm -v .cache
removed '.cache'
aleksandr@MacBook-Air:~$ rm logs
rm: cannot remove 'logs': Is a directory
startup/stage5_all.txt:17: строка пропущена
aleksandr@MacBook-Air:~$ rm -d logs
rm: cannot remove 'logs': Directory not empty
startup/stage5_all.txt:18: строка пропущена
aleksandr@MacBook-Air:~$ rm -rf /
rm: refusing to remove the root directory '/'
startup/stage5_all.txt:24: строка пропущена
aleksandr@MacBook-Air:~$ cd logs/2026
aleksandr@MacBook-Air:~/logs/2026$ rm -rf /logs
rm: cannot remove '/logs': it is or contains the current directory
startup/stage5_all.txt:33: строка пропущена
aleksandr@MacBook-Air:~/logs/2026$ cd
aleksandr@MacBook-Air:~$ rm -v nope readme.txt logs
removed 'readme.txt'
rm: cannot remove 'nope': No such file or directory
rm: cannot remove 'logs': Is a directory
startup/stage5_all.txt:38: строка пропущена
aleksandr@MacBook-Air:~$ rm -rv logs
removed 'logs/2026/feb.log'
removed 'logs/2026/jan.log'
removed directory 'logs/2026'
removed directory 'logs'
aleksandr@MacBook-Air:~$ rm -rf work nope
aleksandr@MacBook-Air:~$ vfs-tree
rm_demo/
aleksandr@MacBook-Air:~$ exit

vfs_examples/rm_demo
vfs_examples/rm_demo/.cache
vfs_examples/rm_demo/cache
vfs_examples/rm_demo/cache/index.txt
vfs_examples/rm_demo/logs
...
```

В конце сценария VFS в памяти пуста, а на диске все файлы на месте.

Выполнение стартового скрипта (`./scripts/run_all.sh`): ошибочные
строки пропускаются, выполнение продолжается.

```text
=== Параметры эмулятора ===
VFS:    vfs_examples/minimal
Script: startup/stage2_errors.txt
===========================
VFS загружена: корень 'minimal', папок: 0, файлов: 1, байт: 212
aleksandr@MacBook-Air:~$ ls -l
- 212 readme.txt
aleksandr@MacBook-Air:~$ foo bar
foo: command not found
startup/stage2_errors.txt:3: строка пропущена
aleksandr@MacBook-Air:~$ cd /
aleksandr@MacBook-Air:~$ cd a b
cd: too many arguments
startup/stage2_errors.txt:5: строка пропущена
aleksandr@MacBook-Air:~$ ls -a
.
..
readme.txt
aleksandr@MacBook-Air:~$
```

Скрипт с командой `exit` (`./scripts/run_exit_script.sh`):

```text
aleksandr@MacBook-Air:~$ ls -a
.
..
readme.txt
aleksandr@MacBook-Air:~$ exit 0
```

Строка `ls -l` после `exit` не выполняется, REPL не открывается.

Загрузка многоуровневой VFS (`./scripts/run_vfs_deep.sh`):

```text
=== Параметры эмулятора ===
VFS:    vfs_examples/deep
Script: startup/stage3_all.txt
===========================
VFS загружена: корень 'deep', папок: 5, файлов: 5, байт: 230
aleksandr@MacBook-Air:~$ ls $NOPE
docs
readme.txt
src
...
aleksandr@MacBook-Air:~$ vfs-tree
deep/
|-- docs/
|   |-- guide.txt (49 Б)
|   |-- images/
|   |   `-- logo.bin (8 Б)
|   `-- notes/
|       `-- 2026/
|           `-- plan.txt (65 Б)
|-- readme.txt (60 Б)
`-- src/
    `-- main.txt (48 Б)
```

Ошибка загрузки VFS (`./scripts/run_vfs_not_dir.sh`):

```text
vfs: vfs_examples/minimal/readme.txt: источник VFS должен быть каталогом
aleksandr@MacBook-Air:~$
```

Эмулятор продолжает работу без VFS (с пустым корнем), команда
`vfs-tree` сообщит `vfs-tree: VFS не загружена`.
