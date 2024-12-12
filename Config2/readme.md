# Dependency Graph Visualizer

Это программа для построения графа зависимостей пакетов с использованием `apk` и визуализации графа с помощью Graphviz.

## Требования

- Python 3.7 или выше
- Установленный Graphviz
- Утилита `apk` для управления пакетами Alpine Linux

## Установка

1. Убедитесь, что Python и pip установлены на вашей системе.
2. Установите библиотеку `graphviz` для Python:

   ```bash
   pip install graphviz
   ```
3. Убедитесь, что `Graphviz` установлен и добавлен в переменную окружения PATH.

   - Для Linux:

     ```bash
     sudo apt install graphviz
     ```
   - Для macOS:

     ```bash
     brew install graphviz
     ```
   - Для Windows:
     Скачайте и установите [Graphviz](https://graphviz.org/download/).

## Запуск программы

Для запуска программы выполните следующую команду:

```bash
python script.py <visualizer_path> <package_name> <max_depth> [repo_url]
```

- `<visualizer_path>`: путь к исполняемому файлу Graphviz (например, `dot`).
- `<package_name>`: имя пакета, для которого строится граф зависимостей.
- `<max_depth>`: максимальная глубина анализа зависимостей.
- `[repo_url]`: (опционально) URL репозитория пакетов.

### Пример:

```bash
python script.py /usr/bin/dot bash 2 http://dl-cdn.alpinelinux.org/alpine/v3.18/main
```

После выполнения программы граф зависимостей будет сохранен в файл `dependency_graph.png` и открыт автоматически.

## Тестирование

Для проверки работы программы можно написать тестовый скрипт. Пример теста:

```python
import subprocess
import os

def test_get_dependencies():
    result = subprocess.run([
        "python", "script.py", "/usr/bin/dot", "bash", "1", "http://dl-cdn.alpinelinux.org/alpine/v3.18/main"
    ], capture_output=True, text=True)

    assert result.returncode == 0, "Программа завершилась с ошибкой"
    assert os.path.exists("dependency_graph.png"), "Файл с графом не был создан"

    print("Тест пройден: Граф зависимостей создан успешно")

if __name__ == "__main__":
    test_get_dependencies()
```

Запустите этот скрипт, чтобы проверить, что программа корректно выполняет свои задачи.

## Замечания

1. Программа предполагает использование утилиты `apk` из Alpine Linux. Убедитесь, что она доступна в вашей системе.
2. Убедитесь, что Graphviz настроен правильно, чтобы избежать проблем с генерацией графа.


