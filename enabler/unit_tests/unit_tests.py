import unittest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from enabler.cli import CLI
import os


class TestVersionCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('enabler.commands.cmd_version.cli')
    def test_version_command(self, mock_cli):
        # Create an instance of the CLI class
        cli_instance = CLI(self.runner)
        mock_cli.return_value = 'Enabler 0.1\n'
        result = cli_instance.version_command()
        self.assertEqual(result.strip(), 'Enabler 0.1')


class TestSetupCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('enabler.commands.cmd_setup.os')
    @patch('enabler.commands.cmd_setup.urllib.request')
    def test_init_command(self, mock_urllib, mock_os):
        mock_urllib.urlretrieve.side_effect = lambda url, filename: None
        mock_os.stat.return_value.st_mode = 0o755
        cli_instance = CLI(self.runner)
        result = self.runner.invoke(cli_instance.init)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('All dependencies downloaded to bin/', result.output)

    @patch('enabler.commands.cmd_setup.s')
    @patch('enabler.commands.cmd_setup.docker')
    @patch('enabler.commands.cmd_setup.urllib.request')
    def test_metallb_command(self, mock_urllib, mock_docker, mock_s):
        mock_urllib.urlretrieve.side_effect = lambda url, filename: None
        mock_docker.from_env.return_value.networks.return_value = [
            {'Name': 'kind', 'IPAM': {'Config': [{'Subnet': '172.18.0.0/16'}]}}
        ]  # Mocking docker network info
        mock_s.run.side_effect = [
            MagicMock(returncode=1),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]

        result = self.runner.invoke(CLI.metallb, ['--kube-context', 'mycontext', '--ip-addresspool', '172.18.0.240 - 172.18.0.249']) # noqa
        self.assertEqual(result.exit_code, 0)
        self.assertIn('✓ Metallb installed on cluster.', result.output)

    @patch('enabler.commands.cmd_setup.s')
    def test_istio_command(self, mock_s):
        mock_s.run.side_effect = [
            MagicMock(),
            MagicMock(),
        ]
        result = self.runner.invoke(CLI.istio, ['--kube-context', 'mycontext', 'monitoring-tools'])  # noqa
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Istio installed', result.output)


class TestPreflightCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('enabler.commands.cmd_preflight.s')
    def test_preflight_command(self, mock_s):
        mock_s.run.side_effect = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]

        result = self.runner.invoke(CLI.preflight)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('✓ java jdk 11', result.output)
        self.assertIn('✓ docker', result.output)
        self.assertIn('✓ helm 3', result.output)
        self.assertIn('✓ kind', result.output)
        self.assertIn('✓ skaffold', result.output)
        self.assertIn('✓ kubectl', result.output)
        self.assertIn('✓ istioctl', result.output)


class TestPlatformCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('enabler.commands.cmd_platform.s')
    def test_platform_init_command(self, mock_s):
        mock_s.run.side_effect = [
            MagicMock(),  # Mocking submodule update
        ]
        result = self.runner.invoke(CLI.platform.init, ['all', os.getcwd()])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Platform initialized.', result.output)

    @patch('enabler.commands.cmd_platform.s')
    def test_platform_info_command(self, mock_s):
        mock_s.run.side_effect = [
            MagicMock(),
            MagicMock(),
        ]
        result = self.runner.invoke(CLI.platform.info, ['--kube-context', 'test-context']) # noqa 
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Platform can be accessed through the URL:', result.output) # noqa 

    @patch('enabler.commands.cmd_platform.rsa')
    @patch('enabler.commands.cmd_platform.os')
    def test_platform_keys_command(self, mock_os, mock_rsa):
        mock_os.path.exists.return_value = False
        result = self.runner.invoke(CLI.platform.keys, ['2048'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Keys generated successfully.', result.output)


class TestKindCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('enabler.commands.cmd_kind.kind.kind_get')
    @patch('enabler.commands.cmd_kind.kube.kubectl_info')
    @patch('enabler.commands.cmd_kind.docker')
    def test_create_command(self, mock_docker, mock_kubectl_info, mock_kind_get): # noqa 
        mock_kind_get.return_value = False
        mock_kubectl_info.return_value = True
        result = self.runner.invoke(CLI.create, ['--kube-context', 'test_context', 'kind-cluster.yaml']) # noqa
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Kind cluster \'test_context\' is running', result.output) # noqa 

    @patch('enabler.commands.cmd_kind.kind.kind_get')
    @patch('enabler.commands.cmd_kind.kube.kubectl_info')
    def test_delete_command(self, mock_kubectl_info, mock_kind_get):
        mock_kind_get.return_value = True
        mock_kubectl_info.return_value = False
        result = self.runner.invoke(CLI.delete, ['--kube-context', 'test_context']) # noqa
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Kind cluster \'test_context\' was stopped.', result.output) # noqa

    @patch('enabler.commands.cmd_kind.kind.kind_get')
    @patch('enabler.commands.cmd_kind.kube.kubectl_info')
    def test_status_command(self, mock_kubectl_info, mock_kind_get):
        mock_kind_get.return_value = True
        mock_kubectl_info.return_value = True
        result = self.runner.invoke(CLI.status, ['--kube-context', 'test_context']) # noqa 
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Kind cluster \'test_context\' is running', result.output)  # noqa 

    @patch('enabler.commands.cmd_kind.kind.kind_get')
    @patch('enabler.commands.cmd_kind.kube.kubectl_info')
    def test_start_command(self, mock_kubectl_info, mock_kind_get):
        mock_kind_get.return_value = True
        mock_kubectl_info.return_value = False
        result = self.runner.invoke(CLI.start, ['--kube-context', 'test_context']) # noqa 
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Kind cluster \'test_context\' started!', result.output)

    @patch('enabler.commands.cmd_kind.kind.kind_get')
    def test_stop_command(self, mock_kind_get):
        mock_kind_get.return_value = True
        result = self.runner.invoke(CLI.stop, ['--kube-context', 'test_context']) # noqa 
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Kind cluster \'test_context\' was stopped.', result.output) # noqa 


class TestAppCommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('enabler.commands.cmd_apps.s')
    @patch('enabler.commands.cmd_apps.logger')
    def test_namespace_command(self, mock_logger, mock_s):
        mock_s.run.return_value.returncode = 1
        mock_s.run.return_value.stderr = b''
        result = self.runner.invoke(CLI.ns, ['--kube-context', 'test_context', 'my-namespace']) # noqa
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Created a namespace for my-namespace', result.output)
        self.assertIn('Labeled my-namespace namespace for istio injection', result.output) # noqa

    @patch('enabler.commands.cmd_apps.s')
    @patch('enabler.commands.cmd_apps.logger')
    def test_namespace_command_already_exists(self, mock_logger, mock_s):
        mock_s.run.return_value.returncode = 0
        mock_s.run.return_value.stderr = b''
        result = self.runner.invoke(CLI.ns, ['--kube-context', 'test_context', 'my-namespace']) # noqa 
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Skipping creation of my-namespace namespace', result.output) # noqa
