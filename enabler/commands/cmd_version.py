from enabler.cli import pass_environment, logger
import pkg_resources
import click


# Autocompletion function for the version command
def complete_version(ctx, args, incomplete):
    # List of possible completions
    completions = ['version']
    if incomplete.startswith('v'):
        completions.append('version')
    return [c for c in completions if c.startswith(incomplete)]


@click.group('version', short_help='Get current version of Enabler', invoke_without_command=True) # noqa
@click.pass_context
@pass_environment
def cli(ctx, kube_context_cli):
    """Get current version of Enabler"""
    distribution = pkg_resources.get_distribution("enabler")
    version = distribution.version
    logger.info("Enabler "+version)


# Option for autocomplete
@click.option('--autocomplete', is_flag=True, callback=complete_version, expose_value=False, is_eager=True)  # noqa
def version(self):
    pass
