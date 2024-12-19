# Учебный конфигурационный язык

Эта программа анализирует упрощенный конфигурационный язык, выполняет вычисления и сохраняет результат в формате TOML.

## Требования

- Python 3.7 или выше

## Запуск программы

Программа принимает ввод из стандартного ввода и записывает результат в указанный выходной файл.

### Использование:

```bash
python script.py <output_path>
```

- `<output_path>`: путь к выходному файлу в формате TOML.

### Пример:

Создайте файл `input.txt` со следующим содержимым:

```
set a = 10
set b = 20
set c = {1.0.2.0.3.0}
![ a b + sqrt ]
```

Запустите программу:

```bash
python script.py output.toml < input.txt
```

В результате будет создан файл `output.toml` со следующим содержимым:

```toml
a = 10.0
b = 20.0
c = [1.0, 2.0, 3.0]
result_1 = 14.142135623730951
```

## Тестирование

Для проверки работы программы можно написать тестовый скрипт. Пример теста:

```python
import subprocess
import os

def test_program():
    input_code = """set x = 5
set y = 15
![ x y + ]
"""
    expected_output = """x = 5.0
y = 15.0
result_1 = 20.0
"""

    with open("test_input.txt", "w") as f:
        f.write(input_code)

    subprocess.run(
        ["python", "script.py", "test_output.toml"],
        stdin=open("test_input.txt"),
        check=True
    )

    with open("test_output.toml", "r") as f:
        output = f.read()

    assert output.strip() == expected_output.strip(), "Выходные данные не совпадают"

    os.remove("test_input.txt")
    os.remove("test_output.toml")

    print("Тест пройден: программа работает корректно")

if __name__ == "__main__":
    test_program()
```

Запустите этот скрипт для проверки работы программы. Если тест пройдет успешно, программа работает корректно.

## Замечания

1. Программа использует рекурсивный разбор выражений. Убедитесь, что входной код соответствует описанному синтаксису.
2. В операциях используются идентификаторы, определенные с помощью ключевого слова `set`. Несуществующие идентификаторы вызовут ошибку.
