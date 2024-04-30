from enabler.enabler import logger
import click
import git
import os


def get_repo(repopath):
    """Function to get the repository."""
    if not os.path.exists(repopath):
        logger.critical('The repo path ' + repopath + ' does not exist')
        raise click.Abort()

    try:
        return git.Repo(repopath, odbt=git.GitDB, search_parent_directories=True) # noqa
    except git.InvalidGitRepositoryError:
        logger.critical('The repo path ' + repopath + ' is not a git repo')
        raise click.Abort()


def get_submodules(repo, submodules):
    """Function to get submodules."""
    if submodules == 'all':
        submodules = [submodule.name for submodule in repo.submodules]
    else:
        submodules = submodules.split(',')
    logger.debug('The provided submodules are:')
    logger.debug(submodules)
    return submodules
