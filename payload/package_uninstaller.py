#!/usr/bin/env python
# coding=utf-8
# pylint: disable=broad-except
# Copyright (c) 2016-2018, F5 Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
This module uninstalls iControl LX extension give their RPMs
"""

import sys
import time
import logging
import requests

ICONTROL_TIMEOUT = 300
MODULE_NAME = 'f5_secure_installer'

LOG = logging.getLogger(MODULE_NAME)
LOG.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGSTREAM = logging.StreamHandler(sys.stdout)
LOGSTREAM.setFormatter(FORMATTER)
LOG.addHandler(LOGSTREAM)


def is_icontrol():
    """Determines if the TMOS control plane iControl REST service is running"""
    try:
        return requests.get(
            'http://localhost:8100/shared/echo',
            auth=('admin', '')
        ).json()['stage'] == 'STARTED'
    except Exception:
        return False


def wait_for_icontrol(timeout=None):
    """Blocks until the TMOS control plane iControl REST service is running"""
    if not timeout:
        timeout = ICONTROL_TIMEOUT
    end_time = time.time() + timeout
    while (end_time - time.time()) > 0:
        if is_icontrol():
            return True
        LOG.debug('waiting for iControl REST to become available')
        time.sleep(1)
    return False


def create_uninstall_task(package_name):
    """Issues an iControl LX uninstall task"""
    install_url = 'http://localhost:8100/mgmt/shared/iapp/package-management-tasks'
    install_json = '{ "operation": "UNINSTALL", "packageName": "%s" }' % package_name
    response = requests.post(install_url, auth=(
        'admin', ''), data=install_json)
    if response.status_code < 400:
        response_json = response.json()
        return response_json['id']
    return False


def create_query_extensions_task():
    """Issues an iControl LX query task"""
    query_url = 'http://localhost:8100/mgmt/shared/iapp/package-management-tasks'
    query_json = '{ "operation": "QUERY" }'
    response = requests.post(query_url, auth=(
        'admin', ''), data=query_json)
    if response.status_code < 400:
        response_json = response.json()
        return response_json['id']
    return False


def get_task_status(task_id):
    """Queries the task status of an iControl LX task"""
    task_url = 'http://localhost:8100/mgmt/shared/iapp/package-management-tasks/' + task_id
    response = requests.get(task_url, auth=('admin', ''))
    if response.status_code < 400:
        response_json = response.json()
        if 'errorMessage' in response_json:
            LOG.error('task: %s failed - %s', task_id,
                      response_json['errorMessage'])
        return response_json['status']
    return False


def query_task_until_finished(task_id):
    """Blocks until an iControl LX task finishes or fails"""
    max_attempts = 60
    while max_attempts > 0:
        max_attempts -= 1
        status = get_task_status(task_id)
        LOG.debug("task: %s returned status %s", task_id, status)
        if status and status == 'FINISHED':
            return True
        elif status == 'FAILED':
            return False
        time.sleep(2)


def return_package_task(task_id):
    """Returns the content of an iControl LX task"""
    task_url = 'http://localhost:8100/mgmt/shared/iapp/package-management-tasks/' + task_id
    response = requests.get(task_url, auth=('admin', ''))
    if response.status_code < 400:
        response_json = response.json()
        if 'queryResponse' in response_json:
            return response_json['queryResponse']
        return response_json
    return False


def get_installed_extensions():
    """Queries installed iControl LX extensions"""
    task_id = create_query_extensions_task()
    LOG.debug("task: %s created to query installed extensions", task_id)
    query_task_until_finished(task_id)
    return return_package_task(task_id)


def uninstall_extension(rpm_file):
    """Uninstalls an iControl LX extension"""
    wait_for_icontrol()
    packages = get_installed_extensions()
    for package in packages:
        if rpm_file.startswith(package['packageName']):
            LOG.info("creating iControl REST uninstall task for %s",
                     package['packageName'])
            task_id = create_uninstall_task(package['packageName'])
            LOG.debug("task: %s created", task_id)
            rpm_uninstalled = query_task_until_finished(task_id)
            if rpm_uninstalled:
                sys.exit(0)
            sys.exit(1)
    LOG.error('package for %s not installed', rpm_file)
    sys.exit(1)


if __name__ == "__main__":
    uninstall_extension(sys.argv[1])
