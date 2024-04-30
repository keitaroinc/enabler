from src.enabler.enabler import pass_environment, logger
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

    # Check if keys directory exists
    if not os.path.exists(keys_dir):
        logger.info("Creating key directory...")
        os.makedirs(keys_dir)
    logger.info("Keys directory already exists")

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
    logger.info('Keys generated successfully.')


@cli.command('release', short_help='Make a platform release')
@click.argument('version', type=semver.BasedVersionParamType(), required=True)
@click.argument('submodule_path', required=True, type=click.Path(exists=True))
@click.pass_context
@pass_environment
def release(ctx, kube_context_cli, version, submodule_path):
    """Release platform by tagging platform repo and
    tagging the individual component (git submodule)
    using its respective SHA that the submodule points at"""
    submodule_name = os.path.basename(submodule_path)

    # Get the repository
    repo = get_repo(os.getcwd())
    if not repo:
        click.echo("Repository not found.")
        return

    # Check if submodule exists in the repository
    submodule = next((s for s in repo.submodules if s.name.endswith(submodule_name)), None) # noqa
    if not submodule:
        click.echo(f"Submodule '{submodule_name}' not found in the repository.") # noqa
        return

    # Tag platform at provided version
    platform_tag_name = f"v{version}"
    tag_result = tag_repo(repo, platform_tag_name)

    if tag_result:
        click.echo(f"Platform version: {platform_tag_name}")
    else:
        click.echo("Failed to tag platform")

    submodule_path = os.path.join(repo.working_dir, submodule_path)
    submodule_repo = git.Repo(submodule_path)
    submodule_sha = submodule_repo.head.commit.hexsha
    submodule_tag_name = f"{submodule_name}-{platform_tag_name}"
    tag_result = tag_repo(submodule_repo, submodule_tag_name, submodule_sha)
    if tag_result:
        click.echo(f"{submodule_name} version: {platform_tag_name}")
    else:
        click.echo(f"Failed to tag {submodule_name} at {submodule_sha}")


def tag_repo(repo, tag_name, commit_sha=None):
    try:
        if commit_sha:
            repo.create_tag(tag_name, ref=commit_sha)
        else:
            repo.create_tag(tag_name)
        return True
    except git.GitCommandError as e:
        if "already exists" in str(e):
            return True  # Tag already exists
        logger.error(f"Error tagging repository: {e}")
        return False


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
        You can provide a comma-separated list of submodules
        or you can use 'all' for all submodules"""

    # Get the repo from arguments defaults to cwd
    try:
        repo = get_repo(repopath)
        logger.info("REPO")
        logger.info(repo)
        submodules = get_submodules(repo, submodules)
    except Exception as e: # noqa
        logger.info("An error occurred while getting submodule")

    version_info = []
    # Retrieve version information for each submodule
    for submodule in submodules:
        submodule_path = os.path.join(repo.working_dir, submodule)
        try:
            smrepo = git.Repo(submodule_path)
            tags = smrepo.tags
            # Choose the latest tag as version
            latest_tag = max(tags, key=lambda t: t.commit.committed_datetime)
            version_info.append((submodule, latest_tag.name))
        except Exception as e: # noqa
            version_info.append((submodule, "Error retrieving version"))

    for submodule, version in version_info:
        logger.info(f"{submodule}: {version}")
