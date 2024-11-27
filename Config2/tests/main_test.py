from unittest import TestCase
from unittest.mock import patch, MagicMock


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dependency_visualizer import main


class TestMainProgram(TestCase):
    @patch("dependency_visualizer.subprocess.run")
    @patch("dependency_visualizer.graphviz.Digraph.render")
    @patch("argparse.ArgumentParser.parse_args")
    def test_main(self, mock_args, mock_render, mock_run):
        mock_args.return_value = MagicMock(
            visualizer_path="dot",
            package_name="mypackage",
            max_depth=2,
            repo_url=None,
        )
        mock_run.return_value = MagicMock(stdout="dep1\ndep2\n", returncode=0)
        main()
        mock_render.assert_called_once_with("dependency_graph.png", view=True)
