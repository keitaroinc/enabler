from src.enabler_keitaro_inc.enabler import pass_environment, logger

import click
import subprocess as s


# App group of commands
@click.group('apps', short_help='App commands')
@click.pass_context
@pass_environment
def cli(ctx, kube_context_cli):
    """Application specific commands such as creation of kubernetes
    objects such as namespaces, configmaps etc. The name of the
    context is taken from the option --kube-context
    which defaults to 'keitaro'"""
    pass


# Namespace setup
@cli.command('namespace', short_help='Create namespace')
@click.option('--kube-context',
              help='The kubernetes context to use',
              required=False)
@click.argument('name',
                required=True)
@click.pass_context
@pass_environment
def ns(ctx, kube_context_cli, kube_context, name):
    """Create a namespace with auto-injection"""

    if ctx.kube_context is not None:
        kube_context = ctx.kube_context
    if ctx.kube_context is None and kube_context is None:
        logger.error("--kube-context was not specified")
        raise click.Abort()

    # Create a namespace in kubernetes
    ns_exists = s.run(['kubectl',
                       'get',
                       'ns',
                       name,
                       '--context',
                       'kind-' + kube_context],
                      capture_output=True)
    if ns_exists.returncode != 0:
        try:
            app_ns = s.run(['kubectl',  # noqa
                            'create',
                            'ns',
                            name,
                            '--context',
                            'kind-' + kube_context],
                           capture_output=True, check=True)
            logger.info('Created a namespace for ' + name)
            app_ns_label = s.run(['kubectl',   # noqa
                                  'label',
                                  'namespace',
                                  name,
                                  'istio-injection=enabled',
                                  '--context',
                                  'kind-' + kube_context],
                                 capture_output=True, check=True)
            logger.info('Labeled ' + name + ' namespace for istio injection')
        except s.CalledProcessError as error:
            logger.error('Something went wrong with namespace: ' +
                         error.stderr.decode('utf-8'))
            raise click.Abort()
    else:
        logger.info('Skipping creation of ' + name + ' namespace '
                    'since it already exists.')
