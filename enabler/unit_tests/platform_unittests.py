import unittest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from enabler.commands.cmd_platform import cli as CLI


class TestPlatformCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('enabler.commands.cmd_platform.get_submodules')
    @patch('enabler.commands.cmd_platform.get_repo')
    def test_platform_init_command(self, mock_get_repo, mock_get_submodules):
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_get_submodules.return_value = ['submodule1', 'submodule2']
        with patch('enabler.commands.cmd_platform.click_spinner.spinner'):
            result = self.runner.invoke(CLI, ['platform', 'init', 'all'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('Platform initialized.', result.output)

    @patch('enabler.commands.cmd_platform.s')
    def test_platform_info_command(self, mock_s):
        mock_s.run.side_effect = [
            MagicMock(),
            MagicMock(),
        ]
        result = self.runner.invoke(CLI, ['platform', 'info', '--kube-context', 'test-context']) # noqa
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Platform can be accessed through the URL:', result.output) # noqa

    @patch('enabler.commands.cmd_platform.os.path.exists')
    @patch('enabler.commands.cmd_platform.rsa.generate_private_key')
    def test_platform_keys_command(self, mock_generate_private_key, mock_path_exists): # noqa
        mock_generate_private_key.return_value = MagicMock()
        mock_path_exists.return_value = False
        result = self.runner.invoke(CLI, ['platform', 'keys', '2048'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Keys generated successfully.', result.output)
