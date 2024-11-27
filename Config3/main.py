import re
import sys
import argparse
import math

# Лексический анализ
TOKENS = [
    ("COMMENT_SINGLE", r"\|\|.*"),                          # Однострочные комментарии
    ("COMMENT_MULTI_START", r"\(\*"),                      # Начало многострочного комментария
    ("COMMENT_MULTI_END", r"\*\)"),                        # Конец многострочного комментария
    ("SET", r"set"),                                       # Ключевое слово set
    ("COMPUTE", r"!\[.*?\]"),                              # Константное выражение
    ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),             # Идентификаторы
    ("NUMBER", r"-?\d+(\.\d+)?"),                          # Числа
    ("ARRAY", r"\{.*?\}"),                                 # Массивы
    ("EQUALS", r"="),                                      # Оператор присваивания
    ("WHITESPACE", r"\s+"),                                # Пробелы
    ("UNKNOWN", r"."),                                     # Любой другой символ
]

OPERATORS = {"+": lambda x, y: x + y, "-": lambda x, y: x - y, "*": lambda x, y: x * y}

def tokenize(code):
    tokens = []
    position = 0
    while position < len(code):
        for token_type, pattern in TOKENS:
            match = re.match(pattern, code[position:])
            if match:
                if token_type != "WHITESPACE":
                    tokens.append((token_type, match.group(0)))
                position += len(match.group(0))
                break
        else:
            raise ValueError(f"Unexpected token at position {position}: {code[position]}")
    return tokens

# Синтаксический анализ
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.constants = {}

    def parse(self):
        ast = {}
        while self.position < len(self.tokens):
            token_type, token_value = self.tokens[self.position]
            if token_type == "SET":
                self.position += 1
                name = self.expect("IDENTIFIER")
                self.expect("EQUALS")
                value = self.parse_value()
                self.constants[name] = value  # Сохраняем в словарь констант
                ast[name] = value  # Добавляем в итоговый AST для генерации TOML
            elif token_type == "COMPUTE":
                result = self.compute_expression(token_value)
                ast[f"result_{len(ast) + 1}"] = result
                self.position += 1
            else:
                raise ValueError(f"Unexpected token: {token_value}")
        return ast

    def expect(self, token_type):
        if self.tokens[self.position][0] == token_type:
            value = self.tokens[self.position][1]
            self.position += 1
            return value
        raise ValueError(f"Expected {token_type} but got {self.tokens[self.position][0]}")

    def parse_value(self):
        token_type, token_value = self.tokens[self.position]
        if token_type == "NUMBER":
            self.position += 1
            return float(token_value)
        elif token_type == "ARRAY":
            self.position += 1
            return list(map(float, token_value.strip("{}").split(".")))
        elif token_type == "IDENTIFIER":
            self.position += 1
            return self.constants.get(token_value, token_value)
        else:
            raise ValueError(f"Unexpected value token: {token_type}")

    def compute_expression(self, expression):
        tokens = expression.strip("![]").split()
        stack = []
        for token in tokens:
            if token in OPERATORS:
                b, a = stack.pop(), stack.pop()
                stack.append(OPERATORS[token](a, b))
            elif token == "sqrt":
                stack.append(math.sqrt(stack.pop()))
            elif token.isdigit() or re.match(r"-?\d+(\.\d+)?", token):
                stack.append(float(token))
            else:
                stack.append(self.constants[token])
        return stack[0] if stack else None

# Генерация TOML
def generate_toml(ast, output_path):
    with open(output_path, "w") as f:
        for key, value in ast.items():
            if isinstance(value, list):
                f.write(f"{key} = [{', '.join(map(str, value))}]\n")
            else:
                f.write(f"{key} = {value}\n")

# Основная функция
def main():
    parser = argparse.ArgumentParser(description="Учебный конфигурационный язык")
    parser.add_argument("output", help="Путь к выходному файлу TOML")
    args = parser.parse_args()

    # Читаем код из стандартного ввода
    code = sys.stdin.read()

    # Лексический и синтаксический анализ
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()

    # Генерация TOML
    generate_toml(ast, args.output)

if __name__ == "__main__":
    main()