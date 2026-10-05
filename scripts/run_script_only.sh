#!/bin/sh
# Запуск только с параметром --script: корректный стартовый скрипт.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/run.sh" --script "$ROOT/startup/stage2_ok.txt"
