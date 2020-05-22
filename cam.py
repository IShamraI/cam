#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import difflib
import argparse
import requests

from pathlib import Path

__version__ = '0.0.1'

CFG = { 'artifactory': { 'ce': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-enterprise/com/r3/corda',
                         'os': ''},
        'packages':
        [
            {
            'name': 'corda-{version}.jar',
            'repo_type': 'ce',
            'alias': ['corda', 'ce corda'],
            'link': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-enterprise/com/r3/corda/corda/{version}/corda-{version}.jar'
            },
            {
            'name': 'tools-database-manager-{version}.jar',
            'repo_type': 'ce',
            'alias': ['database-manager', 'tools-database-manager', 'dbmtool'],
            'link': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-enterprise/com/r3/corda/tools-database-manager/{version}/tools-database-manager-{version}.jar'
            }
        ]
    }


logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rpc-client.log'),
    level=logging.INFO)
# Adding STDERR output
logging.getLogger().addHandler(logging.StreamHandler())

ce_link = 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-enterprise/com/r3/corda/corda/{version}/corda-{version}.jar'
os_link = 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-enterprise/com/r3/corda/corda/{version}/corda-{version}.jar'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('package', action='store', help='Name of Corda package')
    parser.add_argument('-t', '--test-version', action='append', help='Used versions', required=True)
    parser.add_argument('-u', '--corda-artifactory-username', help='CORDA_ARTIFACTORY_USERNAME', default=None)
    parser.add_argument('-p', '--corda-artifactory-password', help='CORDA_ARTIFACTORY_PASSWORD', default=None)
    parser.add_argument('-s', '--corda-storage', help='Storage location', default='{0}'.format(os.path.join(str(Path.home()), 'corda_jars_storage')))

    args = parser.parse_args()
    CORDA_ARTIFACTORY_USERNAME = os.getenv('CORDA_ARTIFACTORY_USERNAME', args.corda_artifactory_username)
    CORDA_ARTIFACTORY_PASSWORD = os.getenv('CORDA_ARTIFACTORY_PASSWORD', args.corda_artifactory_password)

    if CORDA_ARTIFACTORY_USERNAME is None:
        logging.error("Please set CORDA_ARTIFACTORY_USERNAME env variable or use -u key")
        sys.exit(1)

    if CORDA_ARTIFACTORY_PASSWORD is None:
        logging.error("Please set CORDA_ARTIFACTORY_PASSWORD env variable or use -p key")
        sys.exit(1)

    all_aliases = []
    for package in CFG['packages']:
        all_aliases += package['alias']

    similar = difflib.get_close_matches(args.package, all_aliases)
    logging.info('Found aliases: {0}'.format(similar))
    if len(similar) == 0:
        logging.error("Can't find {0}".format(args.package))
        sys.exit(1)

    targets = []

    for alias in similar:
        for package in CFG['packages']:
            if alias in package['alias']:
                if package not in targets:
                    targets.append(package)
    logging.info('Found packages: {0}'.format(targets))

    if len(targets) > 1 :
        logging.error("Found more than 1 package using \"{0}\" name.".format(args.package))
        sys.exit(1)

    for version in args.test_version:
        logging.debug('Check if {0} is here'.format(
            targets[0]['name'].format(**{'version': version})
        ))
        full_jar_name = targets[0]['name'].format(**{'version': version})
        jar = os.path.join(args.corda_storage, targets[0]['repo_type'], full_jar_name)
        Path(os.path.join(args.corda_storage, targets[0]['repo_type'])).mkdir(parents=True, exist_ok=True)
        if not os.path.exists(jar):
            url = targets[0]['link'].format(**{'version': version})
            logging.info("Download Corda jar file: {0}".format(full_jar_name))
            with open(jar, 'wb') as lib_file:
                lib_file.write(requests.get(url, auth=(CORDA_ARTIFACTORY_USERNAME, CORDA_ARTIFACTORY_PASSWORD)).content)
        if os.stat(jar).st_size < 1000:
            logging.error("Bad Corda jar file {0}. Size={1}".format(jar, os.stat(jar).st_size))
            os.remove(jar)

if __name__ == '__main__':
    sys.exit(main())