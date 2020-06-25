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
                'alias': ['corda', 'cecorda'],
                'link': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-enterprise/com/r3/corda/corda/{version}/corda-{version}.jar'
            },
            {
                'name': '',
                'repo_type': 'ce',
                'alias': ['jmeter', 'corda-jmeter', 'jmeter-corda'],
                'link': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-enterprise/com/r3/corda/jmeter-corda/{version}/jmeter-corda-{version}-testsuite.zip'
            },
            {
                'name': 'corda-tools-network-bootstrapper-{version}.jar',
                'repo_type': 'ce',
                'alias': ['tools-network-bootstrapper', 'corda-tools-network-bootstrapper', 'network-bootstrapper', 'bootstrapper'],
                'link': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-enterprise/com/r3/corda/corda-tools-network-bootstrapper/{version}/corda-tools-network-bootstrapper-{version}.jar'
            },
            {
                'name': 'corda-tools-ha-utilities-{version}.jar',
                'repo_type': 'ce',
                'alias': ['corda-tools-ha-utilities', 'tools-ha-utilities', 'ha-utilities', 'ha-utils', 'hautilities', 'hautils'],
                'link': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-enterprise/com/r3/corda/corda-tools-ha-utilities/{version}/corda-tools-ha-utilities-{version}.jar'
            },
            {
                'name': 'tools-database-manager-{version}.jar',
                'repo_type': 'ce',
                'alias': ['database-manager', 'tools-database-manager', 'dbmtool'],
                'link': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-enterprise/com/r3/corda/tools-database-manager/{version}/tools-database-manager-{version}.jar'
            },
            {
                'name': 'corda-finance-workflows-{version}.jar',
                'repo_type': 'ce',
                'alias': ['corda-finance-workflows', 'finance-workflows', 'workflows'],
                'link': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-enterprise/com/r3/corda/corda-finance-workflows/{version}/corda-finance-workflows-{version}.jar'
            },
            {
                'name': 'corda-finance-contracts-{version}.jar',
                'repo_type': 'os',
                'alias': ['corda-finance-contracts', 'finance-contracts', 'contracts'],
                'link': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-releases/net/corda/corda-finance-contracts/{version}/corda-finance-contracts-{version}.jar'
            },
            {
                'name': 'corda-testserver-{version}.jar',
                'repo_type': 'ce',
                'alias': ['testserver'],
                'link': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-enterprise/com/r3/corda/corda-testserver/{version}/corda-testserver-{version}.jar'
            },
            {
                'name': 'pki-tool-{version}.zip',
                'repo_type': 'enm',
                'alias': ['pki-tool', 'pkitool'],
                'link': 'https://software.r3.com/artifactory/r3-enterprise-network-manager/com/r3/enm/tools/pki-tool/{version}/pki-tool-{version}.zip'
            },
            {
                'name': 'identitymanager-{version}.zip',
                'repo_type': 'enm',
                'alias': ['identitymanager', 'idman'],
                'link': 'https://software.r3.com/artifactory/r3-enterprise-network-manager/com/r3/enm/services/identitymanager/{version}/identitymanager-{version}.zip'
            },
            {
                'name': 'signer-{version}.zip',
                'repo_type': 'enm',
                'alias': ['signer'],
                'link': 'https://software.r3.com/artifactory/r3-enterprise-network-manager/com/r3/enm/services/signer/{version}/signer-{version}.zip'
            },
            {
                'name': 'networkmap-{version}.zip',
                'repo_type': 'enm',
                'alias': ['networkmap', 'nm'],
                'link': 'https://software.r3.com/artifactory/r3-enterprise-network-manager/com/r3/enm/services/networkmap/{version}/networkmap-{version}.zip'
            },
            {
                'name': 'smr-{version}.zip',
                'repo_type': 'enm',
                'alias': ['smr'],
                'link': 'https://software.r3.com/artifactory/r3-enterprise-network-manager/com/r3/enm/services/smr/{version}/smr-{version}.zip'
            },
            {
                'name': 'angel-{version}.zip',
                'repo_type': 'enm',
                'alias': ['angel'],
                'link': 'https://software.r3.com/artifactory/r3-enterprise-network-manager/com/r3/enm/services/angel/{version}/angel-{version}.zip'
            },
            {
                'name': 'auth-{version}.zip',
                'repo_type': 'enm',
                'alias': ['auth'],
                'link': 'https://software.r3.com/artifactory/r3-enterprise-network-manager/com/r3/enm/services/auth/{version}/auth-{version}.zip'
            },
            {
                'name': 'bundled-{version}.zip',
                'repo_type': 'enm',
                'alias': ['bundled'],
                'link': 'https://software.r3.com/artifactory/r3-enterprise-network-manager/com/r3/enm/services/bundled/{version}/bundled-{version}.zip'
            },
            {
                'name': 'zone-{version}.zip',
                'repo_type': 'enm',
                'alias': ['zone'],
                'link': 'https://software.r3.com/artifactory/r3-enterprise-network-manager/com/r3/enm/services/zone/{version}/zone-{version}.zip'
            },
            {
                'name': 'zoneservice-{version}.zip',
                'repo_type': 'enm',
                'alias': ['zoneservice'],
                'link': 'https://software.r3.com/artifactory/r3-enterprise-network-manager/com/r3/enm/services/zoneservice/{version}/zoneservice-{version}.zip'
            }
        ]
    }


logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cam.log'),
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
    parser.add_argument('-c', '--current-storage', help='Store to current folder', action='store_true')

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
        jar = os.path.join(args.corda_storage, targets[0]['repo_type'], full_jar_name) if not args.current_storage else full_jar_name
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
