from src.enabler_keitaro_inc.enabler import pass_environment, logger

import click
import click_spinner
import subprocess as s
import docker
import ipaddress
import urllib.request
import os
import stat
import tarfile
import yaml
import requests
import semver
import re


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

    # Check if bin folder exists
    check_bin_folder()

    # Figure out what kind of OS are we on
    ostype = os.uname().sysname.lower()

    # Load URLs from the JSON file
    enabler_path = get_path()
    file_path = os.path.join(enabler_path, 'dependencies.yaml')
    with open(file_path, 'r') as f:
        urls = yaml.safe_load(f)

    # Use the URLs
    kubectl_url = urls["kubectl"].format(ostype)
    helm_url = urls["helm"].format(ostype)
    istioctl_url = urls["istioctl"].format(ostype)
    kind_url = urls["kind"].format(ostype)
    skaffold_url = urls["skaffold"].format(ostype)

    with click_spinner.spinner():
        # Download kubectl if not exists
        kubectl_location = 'bin/kubectl'
        if os.path.exists(kubectl_location):
            logger.info(f'kubectl already exists at: {kubectl_location}')
        else:
            logger.info('Downloading kubectl...')
            download_and_make_executable(kubectl_url, kubectl_location, 'kubectl') # noqa

        # Download helm if not exists or update if necessary
        helm_location = 'bin/helm'
        if os.path.exists(helm_location):
            logger.info(f'helm already exists at: {helm_location}')
            update_binary_if_necessary(helm_location, helm_url, ostype)
        else:
            download_and_make_executable(helm_url, helm_location, 'helm')

        # Download istioctl if not exists or update if necessary
        istioctl_location = 'bin/istioctl'
        if os.path.exists(istioctl_location):
            logger.info(f'istioctl already exists at: {istioctl_location}')
            update_binary_if_necessary(istioctl_location, istioctl_url, ostype)
        else:
            download_and_make_executable(istioctl_url, istioctl_location, 'istioctl') # noqa

        # Download kind if not exists or update if necessary
        kind_location = 'bin/kind'
        if os.path.exists(kind_location):
            logger.info(f'kind already exists at: {kind_location}')
            update_binary_if_necessary(kind_location, kind_url, ostype)
        else:
            logger.info('Downloading kind...')
            download_and_make_executable(kind_url, kind_location, 'kind')

        # Download skaffold if not exists
        skaffold_location = 'bin/skaffold'
        if os.path.exists(skaffold_location):
            logger.info(f'skaffold already exists at: {skaffold_location}')
        else:
            logger.info('Downloading skaffold...')
            download_and_make_executable(skaffold_url, skaffold_location, 'skaffold') # noqa

    logger.info('All dependencies downloaded to bin/')
    logger.info('IMPORTANT: Please add the path to your user profile to ' +
                os.getcwd() + '/bin directory at the beginning of your PATH')
    logger.info('$ echo export PATH=' + os.getcwd() + '/bin:$PATH >> ~/.profile') # noqa
    logger.info('$ source ~/.profile')


def get_latest_version_from_github(repo_url, ostype):
    try:
        # Fetch the GitHub releases page
        response = requests.get(repo_url)
        response.raise_for_status()
        latest_version = response.json()["tag_name"]
        if latest_version:
            return latest_version
        else:
            logger.error("Failed to find latest release tag")
            return None
    except requests.exceptions.RequestException as e: # noqa
        logger.info("Latest release not found")
        return None


def get_current_version(binary_location, binary_name):
    if os.path.exists(binary_location):
        filename = os.path.basename(binary_location)
        version = extract_version_from_filename(filename, binary_name)
        return version
    else:
        logger.error(f"Binary {binary_name} not found at location: {binary_location}") # noqa
        return None


def extract_version_from_filename(filename, binary_name):
    if binary_name in filename:
        # Check if the filename contains the binary_name
        if binary_name == "helm" or binary_name == "istioctl":
            match = re.search(r'{}-v(\d+\.\d+\.\d+)'.format(binary_name), filename) # noqa
            if match:
                return match.group(1)
        elif binary_name == "kind":
            match = re.search(r'{}-(\d+\.\d+\.\d+)'.format(binary_name), filename) # noqa
            if match:
                return match.group(1)
    return None


def download_and_make_executable(url, destination, binary_name):
    if binary_name in ['skaffold', 'kind', 'kubectl']:
        urllib.request.urlretrieve(url, destination)
        st = os.stat(destination)
        os.chmod(destination, st.st_mode | stat.S_IEXEC)
        logger.info(f'{os.path.basename(destination)} downloaded and made executable!') # noqa
    elif binary_name in ['helm', 'istioctl']:
        download_and_extract_tar(url, destination, binary_name)


def download_and_extract_tar(url, destination, binary_name):
    tar_filename = f'bin/{binary_name}.tar.gz'
    urllib.request.urlretrieve(url, tar_filename)
    tar = tarfile.open(tar_filename, 'r:gz')
    for member in tar.getmembers():
        if member.isreg():
            member.name = os.path.basename(member.name)
            tar.extract(member, 'bin')
    tar.close()
    os.remove(tar_filename)
    logger.info(f'{binary_name} downloaded and made executable!')


def update_binary_if_necessary(binary_location, binary_url, ostype):
    current_version = get_current_version(binary_location, os.path.basename(binary_url)) # noqa
    latest_version = get_latest_version_from_github(binary_url, ostype)
    if latest_version is not None:
        if semver.compare(current_version, latest_version) < 0:
            logger.info(f"Updating {os.path.basename(binary_location)}...")
            urllib.request.urlretrieve(binary_url, f'{binary_location}.tar.gz')
            tar = tarfile.open(f'{binary_location}.tar.gz', 'r:gz')
            for member in tar.getmembers():
                if member.isreg():
                    member.name = os.path.basename(member.name)
                    tar.extract(member, os.path.dirname(binary_location))
            tar.close()
            os.remove(f'{binary_location}.tar.gz')
            logger.info(f'{os.path.basename(binary_location)} updated!')


# Metallb setup
@cli.command('metallb', short_help='Setup metallb')
@click.option('--kube-context',
              help='The kubernetes context to use',
              required=False)
@click.option('--ip-addresspool',
              help='IP Address range to be assigned to metallb, default is last 10 addresses from kind network.'   # noqa
              'The IP address range should be in the kind network in order for the application to work properly.', # noqa
              required=False)
@click.option('--version',
              help='Version of metallb from bitnami. Default version is 4.6.0',
              default='4.6.0')
@click.pass_context
@pass_environment
def metallb(ctx, kube_context_cli, kube_context, ip_addresspool, version):
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
    except s.CalledProcessError:
        logger.info('Metallb not found. Installing...')
        pass
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
    networks = client.networks()

    # Find the network with name 'kind'
    kind_network = None  # Initialize kind_network outside the loop
    for network in networks:
        if network['Name'] == 'kind':
            kind_network = network
            break

    if kind_network is not None:
        # Do something with kind_network
        logger.info("Kind network found:", kind_network)
        kind_subnet = kind_network['IPAM']['Config'][0]['Subnet']
    else:
        logger.info("Kind network not found.")

    # Extract the last 10 ip addresses of the kind subnet
    ips = [str(ip) for ip in ipaddress.IPv4Network(kind_subnet)]
    metallb_ips = ips[-10:]

    if ip_addresspool is None:
        ip_addresspool = metallb_ips[0] + ' - ' + metallb_ips[-1]
    else:
        # Check if ip address range is in kind network and print out a warning
        ip_range = ip_addresspool.strip().split('-')
        try:
            start_ip = ipaddress.IPv4Address(ip_range[0])
            end_ip = ipaddress.IPv4Address(ip_range[1])
        except Exception:
            logger.error('Incorrect IP address range: ' + ip_addresspool)

        if start_ip not in ipaddress.IPv4Network(kind_subnet) or end_ip not in ipaddress.IPv4Network(kind_subnet): # noqa
            logger.error('Provided IP address range not in kind network.')
            logger.error('Kind subnet is: ' + kind_subnet)
            raise click.Abort()

    # Check if version is 3.x.x and then use config map to install, else if version 4.x.x use CDR file for installing. # noqa
    # And dynamically set the IP Address range in the compatible .yaml file
    if version.split('.')[0] == '3':
        yaml_file_path = 'enabler/metallb-configmap.yaml'
        with open(yaml_file_path, 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)
        modified_string = config['data']['config'][:-32]+ip_addresspool+"\n"
        config['data']['config'] = modified_string

        logger.info('Metallb will be configured in Layer 2 mode with the range: ' + ip_addresspool) # noqa
        updated_yaml = yaml.dump(config, default_flow_style=False)
        with open(yaml_file_path, 'w') as yaml_file:
            yaml_file.write(updated_yaml)

    elif int(version.split('.')[0]) >= 4:
        yaml_file_path = 'metallb-crd.yaml'
        with open(yaml_file_path, 'r') as yaml_file:
            config = list(yaml.safe_load_all(yaml_file))


        logger.info('Metallb will be configured in Layer 2 mode with the range: ' + ip_addresspool) # noqa
        for doc in config:
            if 'kind' in doc and doc['kind'] == 'IPAddressPool':
                doc['spec']['addresses'] = [ip_addresspool]

        with open(yaml_file_path, 'w') as yaml_file:
            yaml.dump_all(config, yaml_file, default_flow_style=False)
    else:
        logger.info('Incompatible format for Metallb version. Please check official versions ') # noqa
    ns_exists = s.run(['kubectl',
                       'get',
                       'ns',
                       'metallb',
                       '--context',
                       'kind-' + kube_context],
                      capture_output=True)
    if ns_exists.returncode != 0:
        try:
            metallb_ns = s.run(['kubectl',  # noqa
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
                              'metallb',
                              '--kube-context',
                              'kind-' + kube_context,
                              '--version',
                              version,
                              'bitnami/metallb',
                              '-n',
                              'metallb',
                              '--wait'],
                             capture_output=True, check=True)

        # Apply configuration from CRD file
        config_metallb = s.run(['kubectl',  # noqa
                                'apply',
                                '-f',
                                yaml_file_path], capture_output=True, check=True) # noqa

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
def istio(ctx, kube_context_cli, kube_context, monitoring_tools):
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
        istio_command = ['istioctl',
                         'manifest',
                         'apply',
                         '-y',
                         '--set',
                         'profile=default']
        if monitoring_tools == 'monitoring-tools':
            monitoring_config = ['--set',
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
        istio_command.append('kind-' + kube_context)
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
        if monitoring_tools == 'monitoring-tools':
            try:
                grafana_virtual_service = s.run(['kubectl', 'apply', '-f', 'grafana-vs.yaml'], capture_output=True, check=True) # noqa
            except Exception as e:
                logger.error('Error setting grafana URL')
                logger.error(str(e))


def get_path():
    enabler_path = os.getcwd()
    return enabler_path


def check_bin_folder():
    enabler_path = os.getcwd()
    full_path = enabler_path + '/bin'
    if not os.path.exists(full_path):
        logger.info("Creating bin folder...")
        os.makedirs(full_path)
    else:
        logger.info("Bin folder already exists. Continue...")
        pass
