import unittest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from enabler.commands.cmd_setup import cli as CLI
import os


class TestSetupCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('enabler.commands.cmd_setup.urllib.request')
    @patch('enabler.commands.cmd_setup.os.stat')
    @patch('enabler.commands.cmd_setup.os.chmod')
    def test_init_command(self, mock_chmod, mock_stat, mock_request):

        permission = 0o755
        os.chmod('enabler/bin', permission)

        mock_request.urlretrieve.side_effect = [
            ('enabler/bin/kubectl', None),
            ('enabler/bin/helm.tar.gz', None),
            ('enabler/bin/istioctl.tar.gz', None),
            ('enabler/bin/kind', None),
            ('enabler/bin/skaffold', None),
        ]
        mock_stat.return_value.st_mode = 0o755
        mock_chmod.return_value = None

        result = self.runner.invoke(CLI, ['init'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('All dependencies downloaded to bin/', result.output)

    @patch('enabler.commands.cmd_setup.docker.from_env')
    @patch('enabler.commands.cmd_setup.docker.networks')
    @patch('enabler.commands.cmd_setup.logger')
    @patch('enabler.commands.cmd_setup.s')
    def test_metallb_command(self, mock_s, mock_logger, mock_networks, mock_from_env):  # noqa
        mock_network = MagicMock()
        mock_network['Name'] = 'kind'
        mock_network['IPAM']['Config'][0]['Subnet'] = '192.168.0.0/24'
        mock_from_env.return_value.networks.return_value = [mock_network]
        mock_s.run.return_value.returncode = 0
        mock_logger.info.return_value = None

        result = self.runner.invoke(CLI, ['metallb'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('✓ Metallb installed on cluster.', result.output)
