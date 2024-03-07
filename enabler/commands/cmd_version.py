from enabler.cli import pass_environment, logger
import pkg_resources
import click

# Command to get the current Enabler version
@click.group('version', short_help='Get current version of Enabler', invoke_without_command=True) # noqa
@click.pass_context
@pass_environment
def cli(ctx, kube_context_cli):
    """Get current version of Enabler"""
    distribution = pkg_resources.get_distribution("enabler")
    version = distribution.version
    logger.info("Enabler "+version)
