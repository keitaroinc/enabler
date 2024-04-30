from enabler.enabler import logger
import subprocess as s


def kubectl_info(cluster):
    # Get kubectl cluster-info
    try:
        logger.debug('Running: `kubectl cluster-info`')
        result = s.run(['kubectl',
                        'cluster-info',
                        '--context',
                        'kind-' + cluster],
                       capture_output=True, check=True)
        logger.debug(result.stdout.decode('utf-8'))
        return True
    except s.CalledProcessError as error:
        logger.debug(error.stderr.decode('utf-8'))
        return False


def kubeconfig_set(cont, cluster):
    # Get mapped control plane port from docker
    port = cont.attrs['NetworkSettings']['Ports']['6443/tcp'][0]['HostPort']
    try:
        logger.debug('Running: `kubectl config set-cluster`')
        result = s.run(['kubectl',
                        'config',
                        'set-cluster',
                        'kind-' + cluster,
                        '--server',
                        'https://127.0.0.1:' + port],
                       capture_output=True, check=True)
        logger.debug(result.stdout.decode('utf-8'))
        return True
    except s.CalledProcessError as error:
        logger.debug(error.stderr.decode('utf-8'))
        return False
