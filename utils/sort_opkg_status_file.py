#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# script to help for upgrade extroot.

import sys


def parse_status_file(f):
    packages = {}

    data = {}
    last_key = ''
    last_value = ''
    for line in f:
        # deal w/ Conffiles
        if line.startswith(' ') and '' == last_value and '' != last_key:
            key, value = line.strip().split(' ', 1)
            data[last_key][key] = value
            continue

        line = line.strip()
        if not line:
            # empty line indicate end with a package
            if data:
                packages[data['Package']] = data
                data = {}
                last_key = ''
                last_value = ''
        else:
            last_key, last_value = line.split(':', 1)
            if '' == last_value:
                data[last_key] = {}
            else:
                data[last_key] = last_value.lstrip(' ')
    if data:
        packages[data['Package']] = data

    return packages


def sort_packages(p):
    return {k: p[k] for k in sorted(p)}


def write_packages(p, f):
    for data in p.values():
        for key, value in data.items():
            if isinstance(value, dict):
                f.write('{0}:\n'.format(key))
                for k, v in value.items():
                    f.write(' {0} {1}\n'.format(k, v))
            else:
                f.write('{0}: {1}\n'.format(key, value))
        f.write('\n')


def dump_packages(p, filename):
    if filename and filename != '-':
        try:
            with open(filename, 'w', encoding='utf-8', newline='\n') as f:
                write_packages(p, f)
        except Exception as e:
            print('write failed')
            print(e)
    else:
        write_packages(p, sys.stdout)


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
        description='list user-installed opkg packages')
    parser.add_argument('-o', '--output', help='output file')
    parser.add_argument(
        'status_file',
        type=argparse.FileType('r', encoding='UTF-8'),
        help='opkg status file, from /usr/lib/opkg/status or opkg status')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    packages = parse_status_file(args.status_file)
    packages = sort_packages(packages)
    dump_packages(packages, args.output)
