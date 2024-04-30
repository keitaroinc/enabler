from src.enabler_keitaro_inc.enabler import pass_environment, logger
from src.enabler_keitaro_inc.helpers import kind, kube

import click
import click_spinner
import subprocess as s
import docker
import os
from time import sleep
import socket


# Kind group of commands
@click.group('kind', short_help='Manage kind clusters')
@click.pass_context
@pass_environment
def cli(ctx, kube_context_cli):
    """Manage kind clusters.
    The name of the cluster is taken from the option --kube-context
    """
    pass


@cli.command('create', short_help='Create cluster')
@click.argument('configfile',
                type=click.Path(exists=True),
                default='kind-cluster.yaml')
@click.option('--kube-context',
              help='The kubernetes context to use',
              required=False)
@click.pass_context
@pass_environment
def create(ctx, kube_context_cli, kube_context, configfile):
    if ctx.kube_context is not None:
        kube_context = ctx.kube_context
    if ctx.kube_context is None and kube_context is None:

        logger.error("--kube-context was not specified")
        raise click.Abort()
    # Check if config file exists
    base_name, extension = os.path.splitext(configfile)
    if not os.path.exists(configfile) or extension != '.yaml':
        logger.error('Config file not found.')
        raise click.Abort()
    kind_configfile_validation(configfile)

    # Check if kind cluster is already created
    if kind.kind_get(kube_context):
        logger.error('Kind cluster \'' + kube_context + '\' already exists')
        raise click.Abort()
    try:
        logger.debug('Running: `kind create cluster`')
        create_cluster = s.run(['kind',  # noqa
                                'create',
                                'cluster',
                                '--name',
                                kube_context,
                                '--config',
                               click.format_filename(configfile)],
                               capture_output=False, check=True)
    except s.CalledProcessError as error:
        logger.critical('Could not create kind cluster: ' + str(error))


@cli.command('delete', short_help='Delete cluster')
@click.option('--kube-context',
              help='The kubernetes context to use',
              required=False)
@click.pass_context
@pass_environment
def delete(ctx, kube_context_cli, kube_context):
    """Delete a kind cluster"""
    # Check if the kind cluster exists
    if ctx.kube_context is not None:
        kube_context = ctx.kube_context
    if ctx.kube_context is None and kube_context is None:
        logger.error("--kube-context was not specified")
        raise click.Abort()
    if not kind.kind_get(kube_context):
        logger.error('Kind cluster \'' + kube_context + '\' doesn\'t exist')
        raise click.Abort()

    # Delete the kind cluster
    try:
        logger.debug('Running: `kind delete cluster`')
        create_cluster = s.run(['kind',  # noqa
                                'delete',
                                'cluster',
                                '--name',
                                kube_context],
                               capture_output=False, check=True)
    except s.CalledProcessError as error:
        logger.critical('Could not delete kind cluster:' + str(error))


@cli.command('status', short_help='Cluster status')
@click.option('--kube-context',
              help='The kubernetes context to use',
              required=False)
@click.pass_context
def status(ctx, kube_context):
    """Check the status of the kind cluster"""
    if kube_context is not None:
        if kind.kind_get(kube_context):
            if kube.kubectl_info(kube_context):
                logger.info('Kind cluster \'' + kube_context + '\' is running')
            else:
                logger.error('Cluster not running. Please start the cluster')
                raise click.Abort()
        else:
            logger.error('Kind cluster \'' + kube_context + '\' does not exist.') # noqa
    else:
        logger.error('No kube-context provided.')


@cli.command('start', short_help='Start cluster')
@click.option('--kube-context',
              help='The kubernetes context to use',
              required=False)
@click.pass_context
@pass_environment
def start(ctx, kube_context_cli, kube_context):
    """Start kind cluster"""

    # Kind creates containers with a label io.x-k8s.kind.cluster
    # Kind naming is clustername-control-plane and clustername-worker{x}
    # The idea is to find the containers check status and ports
    # and start them then configure kubectl context

    if ctx.kube_context is not None:
        kube_context = ctx.kube_context
    if ctx.kube_context is None and kube_context is None:
        logger.error("--kube-context was not specified")
        raise click.Abort()

    kind_cp = kube_context + '-control-plane'
    kind_workers = kube_context + '-worker'

    # Check if the cluster exists
    if kind.kind_get(kube_context):
        if kube.kubectl_info(kube_context):
            logger.info('Kind cluster \'' + kube_context + '\' is running')
        else:
            # Check and start kind cluster docker containers
            client = docker.from_env()
            kind_containers = client.containers.list(
                            all, filters={'label': 'io.x-k8s.kind.cluster'})
            with click_spinner.spinner():
                for container in kind_containers:
                    if kind_cp in container.name:
                        if container.status != 'running':
                            container.start()
                            logger.debug('Container ' +
                                         container.name + ' started')
                            container = client.containers.get(container.id)
                            # Configure kubeconfig
                            if kube.kubeconfig_set(container, kube_context):
                                logger.debug('Reconfigured kubeconfig')
                            else:
                                logger.critical('Couldnt configure kubeconfig')
                                raise click.Abort()
                        else:
                            logger.debug('Container ' + container.name +
                                         ' is running')
                            if kube.kubeconfig_set(container, kube_context):
                                logger.debug('Reconfigured kubeconfig')
                            else:
                                logger.critical('Couldnt configure kubeconfig')
                                raise click.Abort()
                    elif kind_workers in container.name:
                        container.start()
                        logger.info('Container ' + container.name + ' started')
                # It takes a while for the cluster to start
                logger.debug('Cluster components started. '
                             'Waiting for cluster to be ready')
                tries = 1
                while not kube.kubectl_info(kube_context) and tries < 10:
                    sleep(30)
                    tries += 1
            if kube.kubectl_info(kube_context):
                logger.debug('Kind cluster ' + kube_context + ' started!')
            else:
                logger.error('Couldn\'t start kind cluster ' + kube_context)
    else:
        logger.error('Kind cluster \'' + kube_context + '\' does not exist.')
        logger.error('Please create a cluster with "enabler kind create"')


@cli.command('stop', short_help='Stop cluster')
@click.option('--kube-context',
              help='The kubernetes context to use',
              required=False)
@click.pass_context
@pass_environment
def stop(ctx, kube_context_cli, kube_context):
    """Stop kind cluster"""
    # Check if the cluster exists
    if ctx.kube_context is not None:
        kube_context = ctx.kube_context
    if ctx.kube_context is None and kube_context is None:
        logger.error("--kube-context was not specified")
        raise click.Abort()

    # Kind creates containers with a label io.x-k8s.kind.cluster
    # Kind naming is clustername-control-plane and clustername-worker{x}
    # The idea is to find the containers and stop them
    kind_cp = kube_context + '-control-plane'
    kind_workers = kube_context + '-worker'

    if kind.kind_get(kube_context):
        # Check and stop kind cluster docker containers
        client = docker.from_env()
        kind_containers = client.containers()
        with click_spinner.spinner():
            for container_info in kind_containers:
                container_name = container_info['Names'][0]
                if container_name and (kind_cp in container_name or kind_workers in container_name): # noqa
                    container_state = container_info['State'][0]
                    if container_state == 'running':
                        container_info.stop()
                        logger.debug('Container ' + container_name + ' stopped') # noqa
                    else:
                        logger.debug('Container ' + container_name + ' is already stopped') # noqa
        logger.info('Kind cluster ' + kube_context + ' was stopped.')
    else:
        logger.error('Kind cluster \'' + kube_context + '\' does not exist.')


# Functions to check if config file has neccessary fields
# and localhost port is free
def kind_configfile_validation(configfile):
    """Validates kind-cluster.yaml file"""

    # Get content of configfile
    with open(configfile, 'r') as yaml_file:
        yaml_content = yaml_file.read()

    keywords_to_check = ['kind', 'apiVersion', 'nodes']
    lines = yaml_content.split('\n')
    keywords_in_file = []
    for line in lines:
        index = line.find('hostPort:')
        if index != -1:
            line_content = line.strip().split(" ")
            port = line_content[1]
            if check_if_port_is_free(int(port)) is not True:
                logger.warn("Possible port conflict on hostPort: " + port
                            + ' in ' + configfile + '.')
                pass

        # Check if all key parameters are present and at level 1
        for key in keywords_to_check:
            if f'{key}:' in line[0:len(key)+1]:
                keywords_in_file.append(key)

    # Get only unique key words that are missing from yaml
    difference = list(set(keywords_to_check) - set(keywords_in_file))
    missing_string = ",".join(difference)

    if len(difference) == 1:
        logger.warn("Field "+missing_string+" missing in "+configfile+'.')
    elif len(difference) >= 2:
        logger.warn("Fields "+missing_string+" missing in "+configfile+'.')


def check_if_port_is_free(port_number):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.bind(("127.0.0.1", port_number))
            s.listen(1)
    except (socket.error, ConnectionRefusedError):
        return False

    return True
