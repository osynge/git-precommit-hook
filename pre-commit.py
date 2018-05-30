#!/usr/bin/python

# Code derived from work shown here
#
#   https://dzone.com/articles/why-your-need-git-pre-commit
#
# If you do not want to invoke this git hook use:
#
#   git commit --no-verify

import os
import re
import subprocess
import sys

modified = re.compile('^(?:M|A)(\s+)(?P<name>.*)')

CHECKS = [
    {
        'output': 'Checking for pdbs...',
        'command': 'grep -n "import pdb" %s',
        'ignore_files': ['.*pre-commit'],
        'match_files': ['.*\.py$'],
        'print_filename': True,
    },
    {
        'output': 'Checking for ipdbs...',
        'command': 'grep -n "import ipdb" %s',
        'ignore_files': ['.*pre-commit'],
        'match_files': ['.*\.py$'],
        'print_filename': True,
    },
    {
        'output': 'Checking for print statements...',
        'command': 'grep -n print %s',
        'match_files': ['.*\.py$'],
        'ignore_files': [
            '.*migrations.*',
            '.*management/commands.*',
            '.*manage.py',
            '.*/scripts/.*'],
        'print_filename': True,
    },
    {
        'output': 'Checking for console.log()...',
        'command': 'grep -n console.log %s',
        'match_files': ['.*yipit/.*\.js$'],
        'print_filename': True,
    },
    {
        'output': 'Checking for debugger...',
        'command': 'grep -n debugger %s',
        'match_files': ['.*\.js$'],
        'print_filename': True,
    },
    {
        'output': 'Running Jshint...',
        # By default, jshint prints 'Lint Free!' upon success.
        # We want to filter this out.
        'command': 'jshint %s | grep -v "Lint Free!"',
        'match_files': ['.*yipit/.*\.js$'],
        'print_filename': False,
    },
    {
        'output': 'Running Pyflakes...',
        'command': 'pyflakes %s',
        'match_files': ['.*\.py$'],
        'ignore_files': ['.*settings/.*', '.*manage.py', '.*migrations.*', '.*/terrain/.*'],
        'print_filename': False,
    },
    {
        'output': 'Running pep8...',
        'command': 'pep8 -r --ignore=E501,W293 %s',
        'match_files': ['.*\.py$'],
        'ignore_files': ['.*migrations.*'],
        'print_filename': False,
    },
    {
        'output': 'Checking for Sass changes...',
        'command': 'sass --quiet --update %s',
        'match_files': ['.*\.scss$'],
        'print_filename': True,
    },
    {
        'output': 'Checking rustfmt...',
        'command': 'rustfmt %s',
        'ignore_files': ['.*/vendor/.*'],
        'match_files': ['.*\.rs$'],
        'print_filename': True,
    },
    {
        'output': 'Checking shellcheck...',
        'command': 'shellcheck %s',
        'match_files': ['.*\.sh$'],
        'print_filename': True,
    },
    {
        'output': 'Checking golint...',
        'command': 'golint %s',
        'match_files': ['.*\.go$'],
        'print_filename': True,
    },
    {
        'output': 'Checking yamllint...',
        'command': 'yamllint %s',
        'match_files': ['.*\.sls$'],
        'print_filename': True,
    }
]


def add_file_filters():
    for i in range(0, len(CHECKS)):
        check_keys = CHECKS[i].keys()
        if 'match_files' not in check_keys:
            print 'addding filter'
            CHECKS[i]['match_all'] = True
            continue
        CHECKS[i]['match_all'] = False
        if 'match_files' in check_keys:
            CHECKS[i]['match_files_compiled'] = []
            for regex in CHECKS[i]['match_files']:
                try:
                    compiled_regex = re.compile(regex)
                except re.error:
                    print 'Warning match_files error parsing regex:%s' % (regex)
                    continue
                CHECKS[i]['match_files_compiled'].append(compiled_regex)

        else:
            CHECKS[i]['match_files_compiled'] = []
        if 'ignore_files' in check_keys:
            relist = []
            for regex in CHECKS[i]['ignore_files']:
                try:
                    compiled_regex = re.compile(regex)
                except re.error:
                    print 'Warning ignore_files error parsing regex:%s' % (regex)
                    continue
                relist.append(compiled_regex)
            CHECKS[i]['ignore_files_compiled'] = relist
        else:
            CHECKS[i]['ignore_files_compiled'] = []


def filter_file(filename):
    test_list = set([])
    for i in range(0, len(CHECKS)):
        check_keys = CHECKS[i].keys()
        if 'ignore_files_compiled' in check_keys:
            ignore = False
            for j in range(0, len(CHECKS[i]['ignore_files_compiled'])):
                if CHECKS[i]['ignore_files_compiled'][j].match(filename):
                    ignore = True
            if ignore:
                continue
        if 'match_all' in check_keys:
            if CHECKS[i]['match_all'] is True:
                print i
                test_list.add(i)
                continue
        check_keys = CHECKS[i].keys()
        if 'match_files_compiled' in check_keys:
            for j in range(0, len(CHECKS[i]['match_files_compiled'])):
                if not CHECKS[i]['match_files_compiled'][j].match(filename):
                    continue
                test_list.add(i)
            if len(test_list) == 0:
                continue
    return test_list


def filterfiles(inputfiles):
    output = {}
    for filename in inputfiles:
        test_list = filter_file(filename)
        if len(test_list) == 0:
                continue
        output[filename] = test_list
    return output


def runcheck(file_name, check_number):
    result = 0
    process = subprocess.Popen(CHECKS[check_number]['command'] % file_name, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    if out or err:
        print CHECKS[check_number]['command'] % file_name
        if CHECKS[check_number]['print_filename']:
            prefix = '\t%s:' % file_name
        else:
            prefix = '\t'
        output_lines = ['%s%s' % (prefix, line) for line in out.splitlines()]
        print '\n'.join(output_lines)
        if err:
            print err
        result = 1
    return result


def main(all_files):
    files = []
    if all_files:
        for root, dirs, file_names in os.walk('.'):
            for file_name in file_names:
                files.append(os.path.join(root, file_name))
    else:
        p = subprocess.Popen(['git', 'diff', '--cached', '--name-status'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        for line in out.splitlines():
            match = modified.match(line)
            if match:
                files.append(match.group('name'))
    result = 0
    files_filtered = filterfiles(files)
    for filename in files_filtered.keys():
        for check in files_filtered[filename]:
            check_rc = runcheck(filename, check)
            if check_rc != 0:
                result = check_rc
    return result


if __name__ == '__main__':
    add_file_filters()
    all_files = False
    if len(sys.argv) > 1 and sys.argv[1] == '--all-files':
        import doctest
        doctest.testmod()
        all_files = True
    sys.exit(main(all_files))
