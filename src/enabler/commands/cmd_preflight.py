from src.enabler.enabler import pass_environment, logger

import click
import subprocess as s


@click.command('preflight', short_help='Preflight checks')
@click.pass_context
@pass_environment
def cli(ctx, kube_context_cli):
    """Preflight checks to ensure all tools and versions are present"""
    # Check java
    try:
        java_ver = s.run(['java', '-version'],
                         capture_output=True, check=True)
        # Check that we have java 11
        java_major_ver = java_ver.stderr.decode('utf-8').split()[2].strip('"')
        if java_major_ver[:2] != '11':
            logger.error(
                'Java JDK 11 needed, please change the version of java on your system')  # noqa
        else:
            logger.info('✓ java jdk 11')
            logger.debug(java_ver.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('java not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('java -version returned something unexpected: ' +
                        error.stderr.decode('utf-8'))

    # Check docker
    try:
        docker_ps = s.run(['docker', 'ps'],
                          capture_output=True, check=True)
        logger.info('✓ docker')
        logger.debug(docker_ps.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('docker not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('`docker ps` returned something unexpected: ' +
                        error.stderr.decode('utf-8'))
        logger.critical('Please ensure the docker daemon is running and that '
                        'your user is part of the docker group. See README')

    # Check helm 3
    try:
        helm_ver = s.run(['helm', 'version', '--short'],
                         capture_output=True, check=True)
        # Check that we have helm 3
        if helm_ver.stdout.decode('utf-8')[1] != "3":
            logger.error(
                'Old version of helm detected when running "helm" from PATH.')
        else:
            logger.info('✓ helm 3')
            logger.debug(helm_ver.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('helm not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('helm version returned something unexpected: ' +
                        error.stderr.decode('utf-8'))

    # Check kind
    try:
        kind_ver = s.run(['kind', 'version'],
                         capture_output=True, check=True)
        logger.info('✓ kind')
        logger.debug(kind_ver.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('kind not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('kind version returned something unexpected: ' +
                        error.stderr.decode('utf-8'))

    # Check skaffold
    try:
        skaffold_ver = s.run(['skaffold', 'version'],
                             capture_output=True, check=True)
        logger.info('✓ skaffold')
        logger.debug(skaffold_ver.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('skaffold not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('skaffold version returned something unexpected: ' +
                        error.stderr.decode('utf-8'))

    # Check kubectl
    try:
        kubectl_ver = s.run(['kubectl', 'version', '--client=true'],
                            capture_output=True, check=True)
        logger.info('✓ kubectl')
        logger.debug(kubectl_ver.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('kubectl not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('kubectl version returned something unexpected: ' +
                        error.stderr.decode('utf-8'))

    # Check istioctl
    try:
        istioctl_ver = s.run(['istioctl', 'version', '-s', '--remote=false'],
                             capture_output=True, check=True)
        # Check that we have istio 1.5 or higher
        if istioctl_ver.stdout.decode('utf-8')[2] < "5":
            logger.error(
                'Old version of istio detected when running "istioctl" from PATH.')  # noqa
        else:
            logger.info('✓ istioctl')
            logger.debug(istioctl_ver.stdout.decode('utf-8'))
    except FileNotFoundError:
        logger.critical('istioctl not found in PATH.')
    except s.CalledProcessError as error:
        logger.critical('istioctl version returned something unexpected: ' +
                        error.stderr.decode('utf-8'))
