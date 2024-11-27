from unittest import TestCase
from unittest.mock import patch, MagicMock


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dependency_visualizer import get_dependencies

class TestGetDependencies(TestCase):
    @patch("dependency_visualizer.subprocess.run")
    def test_simple_dependencies(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="dependency1\ndependency2\n", returncode=0
        )
        dependencies = get_dependencies("mypackage", None, 1)
        self.assertEqual(dependencies, ["dependency1", "dependency2"])

    @patch("dependency_visualizer.subprocess.run")
    def test_recursive_dependencies(self, mock_run):
        def mock_subprocess_run(command, *args, **kwargs):
            if "mypackage" in command:
                return MagicMock(stdout="dependency1\ndependency2\n", returncode=0)
            elif "dependency1" in command:
                return MagicMock(stdout="subdep1\n", returncode=0)
            elif "dependency2" in command:
                return MagicMock(stdout="", returncode=0)
            return MagicMock(stdout="", returncode=0)

        mock_run.side_effect = mock_subprocess_run
        dependencies = get_dependencies("mypackage", None, 2)
        self.assertEqual(dependencies, ["dependency1", "subdep1", "dependency2"])
