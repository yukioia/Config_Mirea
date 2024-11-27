import subprocess
import argparse
import graphviz
import sys


# Функция для получения зависимостей пакета с помощью apk
def get_dependencies(package_name, repo_url, depth, current_depth=0, visited=None):
    if visited is None:
        visited = set()

    # Остановка на максимальной глубине
    if current_depth >= depth:
        return []

    # Получаем список зависимостей пакета
    command = ["apk", "info", "--depends", package_name]
    if repo_url:
        command.append(f"--repository={repo_url}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        dependencies = result.stdout.splitlines()
    except subprocess.CalledProcessError:
        print(f"Error: Unable to get dependencies for {package_name}")
        return []

    # Фильтруем уникальные зависимости
    dependencies = [
        dep.strip()
        for dep in dependencies
        if dep.strip() and dep.strip() not in visited
    ]

    visited.add(package_name)

    all_dependencies = []
    for dep in dependencies:
        # Рекурсивно получаем зависимости каждого пакета
        all_dependencies.append(dep)
        all_dependencies.extend(
            get_dependencies(dep, repo_url, depth, current_depth + 1, visited)
        )

    return all_dependencies


# Функция для построения графа зависимостей с использованием Graphviz
def build_dependency_graph(package_name, dependencies):
    dot = graphviz.Digraph(format="png")
    dot.node(package_name, package_name)  # Добавляем узел для основного пакета

    for dep in dependencies:
        dot.node(dep, dep)  # Добавляем узел для каждой зависимости
        dot.edge(package_name, dep)  # Создаем ребро между пакетом и зависимостью

    return dot


# Главная функция для выполнения программы
def main():
    parser = argparse.ArgumentParser(description="Dependency Graph Visualizer")
    parser.add_argument(
        "visualizer_path", type=str, help="Path to the Graphviz executable"
    )
    parser.add_argument("package_name", type=str, help="Name of the package to analyze")
    parser.add_argument(
        "max_depth", type=int, help="Maximum depth of dependency analysis"
    )
    parser.add_argument(
        "repo_url", type=str, help="Repository URL (optional)", nargs="?"
    )

    args = parser.parse_args()

    # Получаем зависимости
    dependencies = get_dependencies(args.package_name, args.repo_url, args.max_depth)

    # Строим граф зависимостей
    dot = build_dependency_graph(args.package_name, dependencies)

    # Сохраняем или отображаем граф
    output_file = "dependency_graph.png"
    dot.render(output_file, view=True)  # Сохраняем изображение и сразу открываем его

    print(f"Graph generated: {output_file}")


if __name__ == "__main__":
    main()
