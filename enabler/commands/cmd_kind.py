from enabler.cli import pass_environment, logger
from enabler.helpers import kind, kube

import click
import click_spinner
import subprocess as s
import docker
import os
from time import sleep

# Kind group of commands
@click.group('kind', short_help='Manage kind clusters')
@click.pass_context
@pass_environment
def cli(ctx, kube_context):
    """Manage kind clusters.
    The name of the cluster is taken from the option --kube-context
    which defaults to 'keitaro'"""
    pass


@cli.command('create', short_help='Create cluster')
@click.argument('configfile',
                type=click.Path(exists=True),
                default='kind-cluster.yaml')
@click.pass_context
@pass_environment
def create(ctx, kube_context, configfile):
    """Create a kind cluster"""
    
    kube_context = ctx.kube_context
    
    #Check if config file exists 
    base_name, extension = os.path.splitext(configfile)
    if not os.path.exists(configfile) or extension!='.yaml':
        logger.error('Config file not found.')
        raise click.Abort()
        
    # Check if kind cluster is already created    
    if kind.kind_get(kube_context):
        logger.error('Kind cluster \'' + kube_context + '\' already exists')
        raise click.Abort()

    # Create the kind cluster
    try:
        logger.debug('Running: `kind create cluster`')
        create_cluster = s.run(['kind',
                                'create',
                                'cluster',
                                '--name',
                                kube_context,
                                '--config',
                                click.format_filename(configfile)],
                               capture_output=False, check=True)
    except s.CalledProcessError as error:
        logger.critical('Could not create kind cluster' +
                        error.stderr.decode('utf-8'))


@cli.command('delete', short_help='Delete cluster')
@click.pass_context
@pass_environment
def delete(ctx, kube_context):
    """Delete a kind cluster"""
    # Check if the kind cluster exists
    kube_context = ctx.kube_context
    if not kind.kind_get(kube_context):
        logger.error('Kind cluster \'' + kube_context + '\' doesn\'t exist')
        raise click.Abort()

    # Delete the kind cluster
    try:
        logger.debug('Running: `kind delete cluster`')
        create_cluster = s.run(['kind',
                                'delete',
                                'cluster',
                                '--name',
                                'vmt123'],
                               capture_output=False, check=True)
    except s.CalledProcessError as error:
        logger.critical('Could not delete kind cluster' +
                        error.stderr.decode('utf-8'))


@cli.command('status', short_help='Cluster status')
@click.pass_context
@pass_environment
def status(ctx, kube_context):
    """Check the status of the kind cluster"""
    # Check if the cluster exists
    kube_context = ctx.kube_context
    if kind.kind_get(kube_context):
        if kube.kubectl_info(kube_context):
            logger.info('Kind cluster \'' + kube_context + '\' is running')
        else:
            logger.error('Cluster not running. Please start the cluster')
            raise click.Abort()
    else:
        logger.error('Kind cluster \'' + kube_context + '\' does not exist.')


@cli.command('start', short_help='Start cluster')
@click.pass_context
@pass_environment
def start(ctx, kube_context):
    """Start kind cluster"""
    # Check if the cluster exists
    kube_context = ctx.kube_context

    # Kind creates containers with a label io.x-k8s.kind.cluster
    # Kind naming is clustername-control-plane and clustername-worker{x}
    # The idea is to find the containers check status and ports
    # and start them then configure kubectl context
    kind_cp = kube_context + '-control-plane'
    kind_workers = kube_context + '-worker'

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
@click.pass_context
@pass_environment
def stop(ctx, kube_context):
    """Stop kind cluster"""
    # Check if the cluster exists
    kube_context = ctx.kube_context

    # Kind creates containers with a label io.x-k8s.kind.cluster
    # Kind naming is clustername-control-plane and clustername-worker{x}
    # The idea is to find the containers and stop them
    kind_cp = kube_context + '-control-plane'
    kind_workers = kube_context + '-worker'

    if kind.kind_get(kube_context):
        # Check and stop kind cluster docker containers
        client = docker.from_env()
        kind_containers = client.containers.list(
                        all, filters={'label': 'io.x-k8s.kind.cluster'})
        with click_spinner.spinner():
            for container in kind_containers:
                if kind_cp in container.name or kind_workers in container.name:
                    if container.status == 'running':
                        container.stop()
                        logger.debug('Container ' + container.name + ' stopped')
                    else:
                        logger.debug('Container ' + container.name +
                                     ' is already stopped')
        logger.info('Kind cluster ' + kube_context + ' was stopped.')
    else:
        logger.error('Kind cluster \'' + kube_context + '\' does not exist.')
