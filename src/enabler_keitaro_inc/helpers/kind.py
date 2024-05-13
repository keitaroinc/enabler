from src.enabler_keitaro_inc.enabler import logger

import click
import subprocess as s


def kind_get(cluster):
    # Get kind clusters
    try:
        logger.debug('Running: `kind get clusters`')
        result = s.run(['kind', 'get', 'clusters'],
                       capture_output=True, check=True)
        kind_clusters = result.stdout.decode('utf-8').splitlines()
        if cluster in kind_clusters:
            return True
        else:
            return False
    except s.CalledProcessError as error:
        logger.critical(error.stderr.decode('utf-8'))
        raise click.Abort()
