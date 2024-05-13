import unittest
import tempfile
import shutil
from click.testing import CliRunner
from unittest.mock import patch
from git import Repo
from src.enabler_keitaro_inc.enabler import cli as CLI
import os


class TestPlatformCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

        # Create a temporary Git repository
        self.repo = Repo.init(self.temp_dir)
        self.repo.git.config('--local', 'user.email', 'test@example.com')
        self.repo.git.config('--local', 'user.name', 'Test')

    def tearDown(self):
        # Clean up the temporary directory after the test
        shutil.rmtree(self.temp_dir)

    @patch('src.enabler_keitaro_inc.commands.cmd_platform.s')
    def test_platform_init(self, mock_s):
        mock_s.run.return_value.returncode = 0
        result = self.runner.invoke(CLI, ['platform', 'init', 'all', self.temp_dir]) # noqa
        self.assertEqual(result.exit_code, 0)

    @patch('src.enabler_keitaro_inc.commands.cmd_platform.s')
    def test_platform_info(self, mock_s):
        mock_s.run.return_value.returncode = 0
        result = self.runner.invoke(CLI, ['platform', 'info', '--kube-context', '']) # noqa
        self.assertEqual(result.exit_code, 0)

    @patch('src.enabler_keitaro_inc.commands.cmd_platform.click.confirm')
    @patch('src.enabler_keitaro_inc.commands.cmd_platform.s')
    def test_platform_keys(self, mock_s, mock_confirm):
        mock_s.run.return_value.returncode = 0
        mock_confirm.return_value = False
        result = self.runner.invoke(CLI, ['platform', 'keys'])
        self.assertEqual(result.exit_code, 0)

    @patch('src.enabler_keitaro_inc.commands.cmd_platform.s')
    def test_platform_release(self, mock_s):
        mock_s.run.return_value.returncode = 0
        simulated_path = 'platform/microservice'
        # Create the simulated path if it doesn't exist
        if not os.path.exists(simulated_path):
            os.makedirs(simulated_path)
        result = self.runner.invoke(CLI, ['platform', 'release', '2.1.7', simulated_path]) # noqa
        self.assertEqual(result.exit_code, 0)

    @patch('src.enabler_keitaro_inc.commands.cmd_platform.s')
    def test_platform_version(self, mock_s):
        mock_s.run.return_value.returncode = 0
        result = self.runner.invoke(CLI, ['platform', 'version'])
        self.assertEqual(result.exit_code, 0)
