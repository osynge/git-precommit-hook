#!/usr/bin/python

import os
import argparse
import logging
import sys


def find_git_repos(search_path):
    log = logging.getLogger("find_git_repos")
    for root, dir_names, file_names in os.walk(search_path):
        for dir_name in dir_names:
            path = os.path.join(root, dir_name)
            path_split = os.path.split(path)
            if not path_split[1] == 'hooks':
                continue
            base_split = os.path.split(path_split[0])
            if not base_split[1] == '.git':
                continue
            repo_path = base_split[0]
            log.debug("Found git repo:%s" % repo_path)
            yield repo_path


def find_git_hook_needed(link_src, search_path):
    log = logging.getLogger("find_git_hook_needed")
    for i in find_git_repos(search_path):
        hook_path = os.path.join(i, '.git/hooks/pre-commit')
        if os.path.exists(hook_path):
            # File exists or symbolic link
            log.debug('hook exists:%s' % (hook_path))
            continue
        if os.path.islink(hook_path):
            # remove broken symlinks
            log.warning('Removing broken symlink:%s' % (hook_path))
            os.remove(hook_path)
        log.info('Creating symlink:%s' % (hook_path))
        os.symlink(link_src, hook_path)


def get_link_src():
    abs_path = os.path.abspath(__file__)
    abs_path_dir = os.path.dirname(abs_path)
    src = os.path.join(abs_path_dir, 'pre-commit.py')
    log = logging.getLogger("get_link_src")
    log.debug('Git hook src:%s' % (src))
    return src


def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='pre-commit-install\n')
    parser.add_argument(
        '--base',
        action='store',
        help='Base path to search for git repos.',
        metavar='DIR')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('--quiet', '-q', action='count')
    parser.add_argument("--logcfg", type=str, help="log configuration file")
    return parser


def main(args=None, namespace=None):
    parser = get_parser()
    args = parser.parse_args(args=args, namespace=namespace)

    # Set up log file
    LoggingLevel = logging.WARNING
    LoggingLevelCounter = 1
    logFile = None
    if args.verbose:
        LoggingLevelCounter = LoggingLevelCounter - args.verbose
    if args.quiet:
        LoggingLevelCounter = LoggingLevelCounter + args.quiet
    if LoggingLevelCounter <= 0:
        LoggingLevel = logging.DEBUG
    if LoggingLevelCounter == 1:
        LoggingLevel = logging.INFO
    if LoggingLevelCounter == 2:
        LoggingLevel = logging.WARNING
    if LoggingLevelCounter == 3:
        LoggingLevel = logging.ERROR
    if LoggingLevelCounter == 4:
        LoggingLevel = logging.FATAL
    if LoggingLevelCounter >= 5:
        LoggingLevel = logging.CRITICAL

    if args.logcfg:
        logFile = args.logcfg
    if logFile is not None:
        if os.path.isfile(logFile):
            logging.config.fileConfig(logFile)
        else:
            logging.basicConfig(level=LoggingLevel)
            log = logging.getLogger("main")
            log.error("Logfile configuration file '%s' was not found." % (args.log_config))
            sys.exit(1)
    else:
        logging.basicConfig(level=LoggingLevel)
    log = logging.getLogger("main")
    base_dir = os.getcwd()
    if args.base:
        base_dir = args.base
    link_src = get_link_src()
    find_git_hook_needed(link_src, base_dir)


if __name__ == "__main__":
    main()
