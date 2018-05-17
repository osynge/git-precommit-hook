#!/usr/bin/python

import os
import argparse


def find_git_repos(search_path):
    repos = []
    for root, dir_names, file_names in os.walk(search_path):
        for dir_name in dir_names:
            path = os.path.join(root, dir_name)
            path_split = os.path.split(path)
            if not path_split[1] == 'hooks':
                continue
            base_split = os.path.split(path_split[0])
            if not base_split[1] == '.git':
                continue
            repos.append(base_split[0])
            yield base_split[0]


def find_git_hook_needed(link_src, search_path):
    search_path = '/home/oms101/home/programming/'
    for i in find_git_repos(search_path):
        hook_path = os.path.join(i, '.git/hooks/pre-commit')
        if os.path.exists(hook_path):
            # File exists or symbolic link
            continue
        if os.path.islink(hook_path):
            # remove broken symlinks
            os.remove(hook_path)
        os.symlink(link_src, hook_path)


def get_link_src():
    abs_path = os.path.abspath(__file__)
    abs_path_dir = os.path.dirname(abs_path)
    return os.path.join(abs_path_dir, 'pre-commit.py')


def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='pre-commit-install\n\n%s')
    parser.add_argument(
        '--base',
        action='store',
        help='Base path to search for git repos.',
        metavar='CONFIG')
    return parser


def main(args=None, namespace=None):
    parser = get_parser()
    args = parser.parse_args(args=args, namespace=namespace)
    
    link_src = get_link_src()
    
    if args.base:
        find_git_hook_needed(link_src, args.base)
