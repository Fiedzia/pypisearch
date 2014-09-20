#!/usr/bin/env python3
import argparse
import json
import os
import sys

from xmlrpc import client as xmlrpcclient

import arrow
import bar
import requests


PYPI = 'http://pypi.python.org/pypi'


def get_pkg(session, run_dir, name, skip_if_exists=False):
    fname = run_dir + '/' + name.lower() + '.json'
    if skip_if_exists:
        try:
            if os.path.exists(fname):
                with open(fname) as f:
                    json.load(f)
                return
        except:
            pass

    pkg_data = session.get(PYPI + '/' + name + '/json').json()
    with open(fname, mode='w') as f:
        json.dump(pkg_data, f, indent=4)


def run():
    client = xmlrpcclient.ServerProxy(PYPI)
    parser = argparse.ArgumentParser(description='pypi index copy')
    parser.add_argument('-r', '--retry-failed', action='store_true',
                        help='Redownload packages that failed last time')
    parser.add_argument('-c', '--continue', action='store_true', dest='_continue',
                        help='Continue. Do not download package if there is local file for it.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()
    run_id = arrow.utcnow().format('YYYY_MM_DD')
    run_dir = 'packages/{}'.format(run_id)
    os.makedirs(run_dir, exist_ok=True)
    os.makedirs(run_dir + '/meta', exist_ok=True)

    if args.retry_failed:
        try:
            fail_fname = run_dir + '/meta/failures.json'
            with open(fail_fname, 'w') as fail_file:
                package_names = json.load(fail_file)['packages']
        except:
            print('Fail file {} is missing or invalid.'.format(fail_fname), file=sys.stderr)
            sys.exit(1)

    else:
        package_names = client.list_packages()
        with open(run_dir + '/meta/all.json', 'w') as all_file:
            json.dump({'packages': package_names}, all_file)
    progressbar = bar.Bar(bar_max=len(package_names))
    session = requests.Session()
    errors = 0
    failed = []

    for name in package_names:
        try:
            get_pkg(session, run_dir, name, skip_if_exists=args._continue)
            progressbar.step()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            failed.append(name)
            errors += 1
    else:
        os.symlink(run_dir, 'packages/latest')
    print('errors: ', errors)
    if failed:
        fail_fname = run_dir + '/meta/failures.json'
        with open(fail_fname, 'w') as fail_file:
            json.dump({'packages': failed}, fail_file, indent=4)

        msg = """Downloading info for {} packages failed.
        Full list is stored in {} file. You can retry by invoking this
        script with -r flag."""

        print(msg.format(len(failed), fail_fname))
if __name__ == '__main__':
    run()
