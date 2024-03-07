from enabler.cli import pass_environment, logger
from enabler.helpers.git import get_submodules, get_repo
from enabler.type import semver

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import click
import click_spinner
import git
import os
import subprocess as s


# App group of commands
@click.group('platform', short_help='Platform commands')
@click.pass_context
@pass_environment
def cli(ctx, kube_context_cli):
    """Platform commands to help with handling the codebase and repo"""
    pass


@cli.command('init', short_help='Initialize platform components')
@click.argument('submodules',
                required=True,
                default='all')
@click.argument('repopath',
                required=True,
                type=click.Path(exists=True),
                default=os.getcwd())
@click.pass_context
@pass_environment
def init(ctx,  kube_context_cli, submodules, repopath):
    """Init the platform by doing submodule init and checkout
    all submodules on master"""

    # Get the repo from arguments defaults to cwd
    repo = get_repo(repopath)

    submodules = get_submodules(repo, submodules)

    with click_spinner.spinner():
        for submodule in submodules:
            try:
                smodule = repo.submodule(submodule)
                smodule.update()
                logger.info('Fetching latest changes for {}'.format(submodule))
            except Exception as e:
                logger.error(f'An error occurred while updating {submodule}: {e}' .format(submodule,e)) # noqa

    logger.info('Platform initialized.')


@cli.command('info', short_help='Get info on platform')
@click.option('--kube-context',
              help='The kubernetes context to use',
              required=False)
@click.pass_context
@pass_environment
def info(ctx,  kube_context_cli, kube_context):
    """Get info on platform and platform components"""
    if ctx.kube_context is not None:
        kube_context = ctx.kube_context
    if ctx.kube_context is None and kube_context is None:
        logger.error("--kube-context was not specified")
        raise click.Abort()
    try:
        gw_url = s.run(['kubectl',
                        '--context',
                        'kind-' + kube_context,
                        '-n',
                        'istio-system',
                        'get',
                        'service',
                        'istio-ingressgateway',
                        '-o',
                        'jsonpath={.status.loadBalancer.ingress[0].ip}'],
                       capture_output=True, check=True)
        logger.info('Platform can be accessed through the URL:')
        logger.info(u'\u2023' + ' http://' + gw_url.stdout.decode('utf-8'))
        kube_info = s.run(['kubectl', 'cluster-info'], capture_output=True, check=True) # noqa
        logger.info(kube_info.stdout.decode('utf-8'))
    except s.CalledProcessError as error:
        logger.error(error.stderr.decode('utf-8'))
        raise click.Abort()


# Generate keys
@cli.command('keys', short_help='Generate keys')
@click.argument('bits',
                required=True,
                default=2048)
@click.pass_context
@pass_environment
def keys(ctx,  kube_context_cli, bits):
    """Generate encryption keys used by the application services"""
    # Locations, we can argument these if need be
    keys_dir = 'infrastructure/keys/'
    private_key_filename = 'key.pem'
    public_key_filename = 'key.pub'

    # Check if the keys exist and warn user
    if (
        os.path.isfile(keys_dir + private_key_filename) or
        os.path.isfile(keys_dir + public_key_filename)
       ):
        if not click.confirm('Keys already exist, overwrite y/n?'):
            raise click.Abort()

    # Generate the keys using cryptography
    logger.info('Generating keys...')
    with click_spinner.spinner():
        key = rsa.generate_private_key(
            backend=default_backend(),
            public_exponent=65537,
            key_size=bits
        )
        private_key = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption())
        public_key = key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        )

    # Write the private key
    f = open(keys_dir + private_key_filename, 'wb')
    f.write(private_key)
    f.close()

    # Write the public key
    f = open(keys_dir + public_key_filename, 'wb')
    f.write(public_key)
    f.close()


@cli.command('release', short_help='Make a platform release')
@click.argument('version',
                type=semver.BasedVersionParamType(),
                required=True)
@click.argument('submodules',
                required=True,
                default='all')
@click.argument('repopath',
                required=True,
                type=click.Path(exists=True),
                default=os.getcwd())
@click.pass_context
@pass_environment
def release(ctx,  kube_context_cli, version, submodules, repopath):
    """Release platform by tagging platform repo and
    tagging all individual components (git submodules)
    using their respective SHA that the submodules point at"""

    # Get the repo from arguments defaults to cwd
    repo = get_repo(repopath)
    submodules = get_submodules(repo, submodules)

    # TODO: Tag platform and all submodules at their respective SHAs
    pass
    # TODO: beautify output, check if remotes are ahead, warn anti-patern


@cli.command('version', short_help='Get all versions of components')
@click.argument('submodules',
                required=True,
                default='all')
@click.argument('repopath',
                required=True,
                type=click.Path(exists=True),
                default=os.getcwd())
@click.pass_context
@pass_environment
def version(ctx, kube_context_cli, submodules, repopath):
    """Check versions of microservices in git submodules
        You can provide a comma separated list of submodules
        or you can use 'all' for all submodules"""

    # Get the repo from arguments defaults to cwd
    try:
        repo = get_repo(repopath)
        submodules = get_submodules(repo, submodules)
    except Exception as e:
        logger.error(f'An error occurred while getting {submodule}: {e}'.format(submodule, e)) # noqa

    # Do something with the submodules
    all_sm_details = []
    with click_spinner.spinner():
        for submodule in submodules:
            logger.debug('Switched to submodule: ' + submodule)
            sm_details = {}
            sm_details['repo'] = submodule
            # Are we on an active branch? on a tag? if not then get sha?
            try:
                smrepo = git.Repo(submodule)
                sm_details['present'] = True
            except git.InvalidGitRepositoryError as error:  # noqa
                logger.warning(submodule + ': not present')
                sm_details['present'] = False
                all_sm_details.append(sm_details)
                continue

            # Get branch
            try:
                branch = smrepo.active_branch.name
                sm_details['branch'] = branch

                # Check if remotes are ahead or behind
                origin = smrepo.remotes.origin
                origin.fetch()
                commits_behind = smrepo.iter_commits(branch +
                                                     '..origin/' + branch)
                commits_ahead = smrepo.iter_commits('origin/' + branch +
                                                    '..' + branch)
                sm_details['commits_ahead'] = sum(1 for c in commits_ahead)
                sm_details['commits_behind'] = sum(1 for c in commits_behind)
            except TypeError as error:
                if smrepo.head.is_detached:
                    commit = smrepo.head.commit.hexsha
                    sm_details['branch'] = 'HEAD detached at ' + str(commit)
                else:
                    logger.error(error)

            # Check if we point to any tags
            points_at_tag = smrepo.git.tag('--points-at', 'HEAD')
            sm_details['tag'] = points_at_tag

            # Get sha of HEAD
            sha = smrepo.head.commit.hexsha
            sm_details['sha'] = sha

            # Add submodule details to the list
            all_sm_details.append(sm_details)

    for sm_details in all_sm_details:
        logger.info(sm_details['repo'] + ':')
        if 'branch' in sm_details:
            logger.info(u'\u2023' + ' Branch: ' + sm_details['branch'])
        logger.info(u'\u2023' + ' SHA: ' + sm_details['sha'])
        if 'tag' in sm_details:
            logger.info(u'\u2023' + ' Tag: ' + str(sm_details['tag']))
        if 'commits_ahead' in sm_details and sm_details['commits_ahead'] > 0:
                logger.info(u'\u2023' + ' Ahead by: ' + str(sm_details['commits_ahead']) + ' commits') # noqa

        if 'commits_behind' in sm_details and sm_details['commits_behind'] > 0:
                logger.info(u'\u2023' + ' Behind by: ' + str(sm_details['commits_behind']) + ' commits') # noqa
