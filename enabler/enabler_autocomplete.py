#!/usr/bin/env python
import argcomplete
import argparse


def apps_namespace_subparser(subparsers):
    parser = subparsers.add_parser('apps')
    parser.add_argument('namespace')


def platform_subparser(subparsers):
    parser = subparsers.add_parser('platform')
    subsubparsers = parser.add_subparsers(dest='platform_command')
    subsubparsers.required = True

    subparser_init = subsubparsers.add_parser('init') # noqa
    subparser_info = subsubparsers.add_parser('info') # noqa
    subparser_keys = subsubparsers.add_parser('keys') # noqa
    subparser_release = subsubparsers.add_parser('release') # noqa
    subparser_version = subsubparsers.add_parser('version') # noqa


def kind_subparser(subparsers):
    parser = subparsers.add_parser('kind')
    subsubparsers = parser.add_subparsers(dest='kind_command')
    subsubparsers.required = True

    subparser_create = subsubparsers.add_parser('create') # noqa 
    subparser_delete = subsubparsers.add_parser('delete') # noqa
    subparser_status = subsubparsers.add_parser('status') # noqa
    subparser_start = subsubparsers.add_parser('start')   # noqa
    subparser_stop = subsubparsers.add_parser('stop')     # noqa


def setup_subparser(subparsers):
    parser = subparsers.add_parser('setup')
    subsubparsers = parser.add_subparsers(dest='setup_command')
    subsubparsers.required = True

    subparser_init = subsubparsers.add_parser('init') # noqa 
    subparser_metallb = subsubparsers.add_parser('metallb') # noqa
    subparser_istio = subsubparsers.add_parser('istio')  # noqa


def version_subparser(subparsers):
    subparsers.add_parser('version')


def preflight_subparser(subparsers):
    subparsers.add_parser('preflight')


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    apps_namespace_subparser(subparsers)
    platform_subparser(subparsers)
    kind_subparser(subparsers)
    setup_subparser(subparsers)
    version_subparser(subparsers)
    preflight_subparser(subparsers)

    argcomplete.autocomplete(parser, exclude=[None])  # Modify this line
    args = parser.parse_args()  # noqa


if __name__ == "__main__":
    main()
