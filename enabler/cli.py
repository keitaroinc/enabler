import os
import logging
import click
import click_log
import subprocess


class CLI:
    def __init__(self, runner):
        self.runner = runner

    def version_command(self):
        try:
            result = subprocess.run(['enabler', 'version'], capture_output=True, text=True, check=True) # noqa
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get version: {e}")


CONTEXT_SETTINGS = dict(auto_envvar_prefix="ENABLER")


class Environment(object):
    def __init__(self):
        self.verbose = False
        self.home = os.getcwd()
        self.kube_context = ''


pass_environment = click.make_pass_decorator(Environment, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands")) # noqa

# Use logging for nicer handling of log output
logger = logging.getLogger(__name__)
click_log.basic_config(logger)


class EnablerCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and filename.startswith("cmd_"):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            mod = __import__(
                "enabler.commands.cmd_{}".format(name), None, None, ["cli"]
            )
        except ImportError:
            return
        return mod.cli


@click.command(cls=EnablerCLI, context_settings=CONTEXT_SETTINGS)
@click.option('--kube-context',
              help='The kubernetes context to use',
              required=False)
@click_log.simple_verbosity_option(logger)
@pass_environment
def cli(ctx, kube_context):
    """Enabler CLI for ease of setup of microservice based apps"""

    ctx.kube_context = kube_context
    logger.debug('Using kube-context: kind-' + str(kube_context))
