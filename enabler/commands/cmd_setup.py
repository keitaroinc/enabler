from enabler.cli import pass_environment, logger

import click
import click_spinner
import subprocess as s
import docker
import ipaddress
import urllib.request
import os
import stat
import tarfile

# Setup group of commands
@click.group('setup', short_help='Setup infrastructure services')
@click.pass_context
@pass_environment
def cli(ctx, kube_context_cli):
    """Setup infrastructure services on kubernetes.
    The name of the context is taken from the option --kube-context
    which defaults to 'keitaro'"""
    pass


# Fetch all binaries for the dependencies
@cli.command('init', short_help='Initialize dependencies')
@click.pass_context
@pass_environment
def init(ctx, kube_context_cli):
    """Download binaries for all dependencies"""

    # Figure out what kind of OS are we on
    ostype = os.uname().sysname.lower()

    # URLs for dependencies
    kubectl_url = 'https://storage.googleapis.com/kubernetes-release/release/v1.17.3/bin/{}/amd64/kubectl'.format(ostype)  # noqa
    helm_url = 'https://get.helm.sh/helm-v3.1.2-{}-amd64.tar.gz'.format(ostype)
    istioctl_url = 'https://github.com/istio/istio/releases/download/1.5.1/istioctl-1.5.1-{}.tar.gz'.format(ostype)  # noqa
    kind_url = 'https://github.com/kubernetes-sigs/kind/releases/download/v0.7.0/kind-{}-amd64'.format(ostype)  # noqa
    skaffold_url = 'https://storage.googleapis.com/skaffold/releases/latest/skaffold-{}-amd64'.format(ostype)  # noqa

    with click_spinner.spinner():
        # Download kubectl and make executable
        logger.info('Downloading kubectl...')
        urllib.request.urlretrieve(kubectl_url, 'bin/kubectl')
        st = os.stat('bin/kubectl')
        os.chmod('bin/kubectl', st.st_mode | stat.S_IEXEC)
        logger.info('kubectl downloaded!')

        # Download helm
        logger.info('Downloading helm...')
        urllib.request.urlretrieve(helm_url, 'bin/helm.tar.gz')
        tar = tarfile.open('bin/helm.tar.gz', 'r:gz')
        for member in tar.getmembers():
            if member.isreg():
                member.name = os.path.basename(member.name)
                tar.extract('helm', 'bin')
        tar.close()
        os.remove('bin/helm.tar.gz')
        logger.info('helm downloaded!')

        # Download istioctl
        logger.info('Downloading istioctl...')
        urllib.request.urlretrieve(istioctl_url, 'bin/istioctl.tar.gz')
        tar = tarfile.open('bin/istioctl.tar.gz', 'r:gz')
        tar.extract('istioctl', 'bin')
        tar.close()
        os.remove('bin/istioctl.tar.gz')
        logger.info('istioctl downloaded!')

        # Download kind and make executable
        logger.info('Downloading kind...')
        urllib.request.urlretrieve(kind_url, 'bin/kind')
        st = os.stat('bin/kind')
        os.chmod('bin/kind', st.st_mode | stat.S_IEXEC)
        logger.info('kind downloaded!')

        # Download skaffold and make executable
        logger.info('Downloading skaffold...')
        urllib.request.urlretrieve(skaffold_url, 'bin/skaffold')
        st = os.stat('bin/skaffold')
        os.chmod('bin/skaffold', st.st_mode | stat.S_IEXEC)
        logger.info('skaffold downloaded!\n')

    logger.info('All dependencies downloaded to bin/')
    logger.info('IMPORTANT: Please add the path to your user profile to ' +
                os.getcwd() + '/bin directory at the beginning of your PATH')
    logger.info('$ echo export PATH=' + os.getcwd() + '/bin:$PATH >> ~/.profile')  # noqa
    logger.info('$ source ~/.profile')


# Metallb setup
@cli.command('metallb', short_help='Setup metallb')
@click.option('--kube-context',
              help='The kubernetes context to use',
              required=False)
@click.pass_context
@pass_environment
def metallb(ctx, kube_context_cli, kube_context):
    """Install and setup metallb on k8s"""
    # Check if metallb is installed
    if ctx.kube_context is not None:
        kube_context = ctx.kube_context
    if ctx.kube_context is None and kube_context is None:
        logger.error("--kube-context was not specified")
        raise click.Abort()

    try:
        metallb_exists = s.run(['helm',
                                'status',
                                'metallb',
                                '-n',
                                'metallb',
                                '--kube-context',
                                'kind-' + kube_context],
                               capture_output=True, check=True)
        logger.info('Metallb is already installed, exiting...')
        logger.debug(metallb_exists.stdout.decode('utf-8'))
        raise click.Abort()
    except s.CalledProcessError as error:
        logger.info('Metallb not found. Installing...')
        pass
    
    #Get repo version
    try:
        metallb_repo_add = s.run(['helm',
                                'repo',
                                'add',
                                'bitnami',
                                'https://charts.bitnami.com/bitnami'],
                               capture_output=True, check=True)
        logger.info('Downloading metallb version ...')
        logger.debug(metallb_repo_add.stdout.decode('utf-8'))
        metallb_repo_add = s.run(['helm',
                                'repo',
                                'update'],
                               capture_output=True, check=True)
        logger.info('Repo update ...')
        logger.debug(metallb_repo_add.stdout.decode('utf-8'))

    except s.CalledProcessError as error:
        logger.info('Metallb repo not found.')
        logger.error(error.stdout.decode('utf-8'))
        raise click.Abort()

    # Get the Subnet of the kind network
    client = docker.from_env()
    kind_network = client.networks.get('kind')
    kind_subnet = kind_network.attrs['IPAM']['Config'][0]['Subnet']
    logger.info('Using kind subnet: ' + kind_subnet)

    # Extract the last 10 ip addresses of the docker bridge subnet
    ips = [str(ip) for ip in ipaddress.IPv4Network(kind_subnet)]
    metallb_ips = ips[-10:]
    logger.info('Metallb will be configured in Layer 2 mode with the range: ' +
                metallb_ips[0] + ' - ' + metallb_ips[-1])

    # Metallb layer2 configuration
    metallb_config = (
                   'configInline.address-pools[0].name=default,'
                   'configInline.address-pools[0].protocol=layer2,'
                   'configInline.address-pools[0].addresses[0]='
                    + metallb_ips[0] + '-' + metallb_ips[-1])

    # Create a namespace for metallb if it doesn't exist
    ns_exists = s.run(['kubectl',
                       'get',
                       'ns',
                       'metallb',
                       '--context',
                       'kind-' + kube_context],
                      capture_output=True)
    if ns_exists.returncode != 0:
        try:
            metallb_ns = s.run(['kubectl',
                                'create',
                                'ns',
                                'metallb',
                                '--context',
                                'kind-' + kube_context],
                               capture_output=True, check=True)
            logger.info('Created a namespace for metallb')
        except s.CalledProcessError as error:
            logger.error('Could not create namespace for metallb: ' +
                         error.stderr.decode('utf-8'))
            raise click.Abort()
    else:
        logger.info('Skipping creation of metallb namespace '
                    'since it already exists.')
    # Install metallb on the cluster
    try:
        helm_metallb = s.run(['helm',
                              'install',
                              '--kube-context',
                              'kind-' + kube_context,
                              'metallb',
                              '--set',
                              metallb_config,
                              '-n',
                              'metallb',
                              '--version',
                              '3.0.12',
                              'bitnami/metallb'],
                             capture_output=True, check=True)

        logger.info('✓ Metallb installed on cluster.')
        logger.debug(helm_metallb.stdout.decode("utf-8"))
    except s.CalledProcessError as error:
        logger.error('Could not install metallb')
        logger.error(error.stderr.decode('utf-8'))



# Istio setup
@cli.command('istio', short_help='Setup Istio')
@click.option('--kube-context',
              help='The kubernetes context to use',
              required=False)
@click.argument('monitoring_tools',
                required=False
                )
@click.pass_context
@pass_environment
def istio(ctx, kube_context_cli,kube_context, monitoring_tools):
    """Install and setup istio on k8s"""
    if ctx.kube_context is not None:
        kube_context = ctx.kube_context
    if ctx.kube_context is None and kube_context is None:
        logger.error("--kube-context was not specified")
        raise click.Abort()

    # Run verify install to check whether we are ready to install istio
    try:
        istio_verify = s.run(['istioctl',
                              'verify-install',
                              '--context',
                              'kind-' + kube_context],
                             capture_output=True, check=True)
        logger.info('Istio pre-check passed. Proceeding with install')
        logger.info(istio_verify.stderr.decode('utf-8'))
    except s.CalledProcessError as error:
        logger.critical('Istio pre-check failed')
        logger.critical(error.stderr.decode('utf-8'))
        raise click.Abort()

    # Install Istio
    logger.info('Installing istio, please wait...')
    with click_spinner.spinner():
        istio_command=['istioctl',
                        'manifest',
                        'apply',
                        '-y',
                        '--set',
                        'profile=default']
        if monitoring_tools=='monitoring-tools':
            monitoring_config=['--set',
                                   'addonComponents.grafana.enabled=true',
                                   '--set',
                                   'addonComponents.kiali.enabled=true',
                                   '--set',
                                   'addonComponents.prometheus.enabled=true',
                                   '--set',
                                   'addonComponents.tracing.enabled=true',
                                   '--set',
                                   'values.kiali.dashboard.jaegerURL=http://jaeger-query:16686',  # noqa
                                   '--set',
                                   'values.kiali.dashboard.grafanaURL=http://grafana:3000']  # noqa
            istio_command.extend(monitoring_config)
            
        istio_command.append('--context')
        istio_command.append('kind-'+ kube_context)
        istio_command.append('--wait')
        try:
            istio_install = s.run(istio_command,
                                  capture_output=True, check=True)
            logger.info('Istio installed')
            logger.debug(istio_install.stdout.decode('utf-8'))
        except s.CalledProcessError as error:
            logger.critical('Istio installation failed')
            logger.critical(error.stderr.decode('utf-8'))
            raise click.Abort()
        if monitoring_tools=='monitoring-tools':
            try:
                grafana_virtual_service=s.run(['kubectl','apply','-f','enabler/grafana-vs.yaml'],
                                  capture_output=True, check=True)
            except Exception as e:
                logger.error('Error setting grafana URL')
                logger.error(str(e))
            
                
