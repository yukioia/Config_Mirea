from unittest import TestCase

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dependency_visualizer import build_dependency_graph


class TestBuildDependencyGraph(TestCase):
    def test_graph_structure(self):
        package_name = "mypackage"
        dependencies = ["dep1", "dep2"]
        graph = build_dependency_graph(package_name, dependencies)

        # Проверка узлов
        self.assertIn(package_name, graph.source)
        self.assertIn("dep1", graph.source)
        self.assertIn("dep2", graph.source)

        # Проверка рёбер
        self.assertIn(f"\t{package_name} -> dep1", graph.source)
        self.assertIn(f"\t{package_name} -> dep2", graph.source)
