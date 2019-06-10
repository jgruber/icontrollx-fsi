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
This module installs iControl LX RPMs
"""

import sys
import time
import requests

def create_install_task(rpm_file_path):
    """Issues an iControl LX install task"""
    install_url = 'http://localhost:8100/mgmt/shared/iapp/package-management-tasks'
    install_json = '{ "operation": "INSTALL", "packageFilePath": "%s" }' % rpm_file_path
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
            print('task %s failed: %s', task_id, response_json['errorMessage'])
        return response_json['status']
    return False


def query_task_until_finished(task_id):
    """Blocks until an iControl LX task finishes or fails"""
    max_attempts = 60
    while max_attempts > 0:
        max_attempts -= 1
        status = get_task_status(task_id)
        print("task: %s returned status %s" % (task_id, status))
        if status and status == 'FINISHED':
            return True
        elif status == 'FAILED':
            return False
        time.sleep(2)


def install_package(rpm_file):
    """Installs an iControl LX RPM package"""
    rpm_path="/var/lib/cloud/fsiverified/%s" % rpm_file
    print("creating installation task for %s" % rpm_file)
    install_task_id = create_install_task(rpm_path)
    print("install task received id: %s" % install_task_id)
    rpm_installed = False
    if install_task_id:
        rpm_installed = query_task_until_finished(install_task_id)
        if rpm_installed:
            # wait for f5-rest-node to restart
            time.sleep(5)
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == "__main__":
    install_package(sys.argv[1])
