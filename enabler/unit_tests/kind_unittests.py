import unittest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from enabler.commands.cmd_kind import cli as CLI


class TestKindCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('enabler.commands.cmd_kind.s')
    def test_create_command(self, mock_s):
        mock_s.run.return_value.returncode = 0
        result = self.runner.invoke(CLI, ['create'])
        self.assertEqual(result.exit_code, 0)

    @patch('enabler.commands.cmd_kind.s')
    def test_delete_command(self, mock_s):
        mock_s.run.return_value.returncode = 0
        result = self.runner.invoke(CLI, ['delete'])
        self.assertEqual(result.exit_code, 0)

    @patch('enabler.commands.cmd_kind.s')
    def test_status_command(self, mock_s):
        mock_s.run.return_value.returncode = 0
        result = self.runner.invoke(CLI, ['status'])
        self.assertEqual(result.exit_code, 0)

    @patch('enabler.commands.cmd_kind.docker')
    @patch('enabler.commands.cmd_kind.kube')
    @patch('enabler.commands.cmd_kind.click_spinner.spinner')
    def test_start_command(self, mock_spinner, mock_kube, mock_docker):
        mock_kube.kubectl_info.return_value = True
        mock_container = MagicMock()
        mock_container.name = 'test-control-plane'
        mock_container.status = 'running'
        mock_docker.from_env.return_value.containers.list.return_value = [mock_container] # noqa
        result = self.runner.invoke(CLI, ['start'])
        self.assertEqual(result.exit_code, 0)

    @patch('enabler.commands.cmd_kind.docker')
    @patch('enabler.commands.cmd_kind.click_spinner.spinner')
    def test_stop_command(self, mock_spinner, mock_docker):
        mock_container = MagicMock()
        mock_container.name = 'test-control-plane'
        mock_container.status = 'running'
        mock_docker.from_env.return_value.containers.list.return_value = [mock_container] # noqa
        result = self.runner.invoke(CLI, ['stop'])
        self.assertEqual(result.exit_code, 0)
