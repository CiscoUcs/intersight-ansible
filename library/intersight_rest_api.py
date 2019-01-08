#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metatdata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: intersight_rest_api
short_description: REST API configuration for Cisco Intersight
description:
- REST API configuration for Cisco Intersight.
- All REST API resources and properties must be directly specified.
- For more information see L(Cisco Intersight,https://intersight.com/help).
extends_documentation_fragment: intersight
options:
  
author:
- David Soper (@dsoper2)
- CiscoUcs (@CiscoUcs)
version_added: '2.8'
'''

EXAMPLES = r'''
- name: Configure Boot Policy
  intersight_rest_api:
    api_private_key: "{{ api_private_key }}"
    api_key_id: "{{ api_key_id }}"
    resource_path: /boot/PrecisionPolicies
    query_params:
      $filter: "Name eq 'vmedia-hdd'"
    api_body: {
        "Name": "vmedia-hdd",
        "BootDevices": [
            {
                "ObjectType": "boot.VirtualMedia",
                "Enabled": true,
                "Name": "remote-vmedia",
                "Subtype": "cimc-mapped-dvd"
            },
            {
                "ObjectType": "boot.LocalDisk",
                "Enabled": true,
                "Name": "boot-lun",
                "Bootloader": null,
                "Slot": "MRAID"
            }
        ],
        "ConfiguredBootMode": "Legacy",
        "EnforceUefiSecureBoot": false
    }
    state: present
- name: Delete Boot Policy
  intersight_rest_api:
    api_private_key: "{{ api_private_key }}"
    api_key_id: "{{ api_key_id }}"
    resource_path: /boot/PrecisionPolicies
    query_params:
      $filter: "Name eq 'vmedia-hdd'"
    state: absent
'''

import re
from ansible.module_utils.remote_management.intersight import IntersightModule, intersight_argument_spec
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems


def get_resource(intersight):
    '''
    GET a resource and return the 1st element found
    '''
    options = {
        'http_method': 'get',
        'resource_path': intersight.module.params['resource_path'],
        'query_params': intersight.module.params['query_params'],
    }
    response_dict = intersight.call_api(**options)
    if response_dict.get('Results'):
        # return the 1st list element
        response_dict = response_dict['Results'][0]

    return response_dict


def compare_values(expected, actual):
    try:
        for (key, value) in iteritems(expected):
            if re.search(r'P(ass)?w(or)?d', key) or not actual.get(key):
                # do not compare any password related attributes or attributes that are not in the actual resource
                continue
            if not compare_values(value, actual[key]):
                return False
        # loop complete with all items matching
        return True
    except (AttributeError, TypeError):
        if expected and actual != expected:
            return False
        return True


def configure_resource(intersight, moid):
    if not intersight.module.check_mode:
        if moid:
            # update the resource - user has to specify all the props they want updated
            options = {
                'http_method': intersight.module.params['update_method'],
                'resource_path': intersight.module.params['resource_path'],
                'body': intersight.module.params['api_body'],
                'moid': moid,
            }
            response_dict = intersight.call_api(**options)
            if response_dict.get('Results'):
                # return the 1st element in the results list
                intersight.result['api_response'] = response_dict['Results'][0]
        else:
            # create the resource
            options = {
                'http_method': 'post',
                'resource_path': intersight.module.params['resource_path'],
                'body': intersight.module.params['api_body'],
            }
            intersight.call_api(**options)
            intersight.result['api_response'] = get_resource(intersight)
    intersight.result['changed'] = True


def delete_resource(intersight, moid):
    # delete resource and create empty api_response
    if not intersight.module.check_mode:
        options = {
            'http_method': 'delete',
            'resource_path': intersight.module.params['resource_path'],
            'moid': moid,
        }
        intersight.call_api(**options)
        intersight.result['api_response'] = {}
    intersight.result['changed'] = True


def main():
    argument_spec = intersight_argument_spec
    argument_spec.update(
        resource_path=dict(type='str', required=True),
        query_params=dict(type='dict', default={}),
        update_method=dict(type='str', choices=['patch', 'post'], default='patch'),
        api_body=dict(type='dict', default={}),
        state=dict(type='str', choices=['absent', 'present'], default='present'),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )

    intersight = IntersightModule(module)
    intersight.result['api_response'] = {}

    # get the current state of the resource
    intersight.result['api_response'] = get_resource(intersight)

    # determine requested operation (config, delete, or neither (get resource only))
    if module.params['state'] == 'present':
        request_delete = False
        # api_body implies resource configuration through post/patch
        request_config = bool(module.params['api_body'])
    else:  # state == 'absent'
        request_delete = True
        request_config = False

    moid = None
    resource_values_match = False
    if (request_config or request_delete) and intersight.result['api_response'].get('Moid'):
        # resource exists and moid was returned
        moid = intersight.result['api_response']['Moid']
        if request_config:
            resource_values_match = compare_values(module.params['api_body'], intersight.result['api_response'])
        else:  # request_delete
            delete_resource(intersight, moid)

    if request_config and not resource_values_match:
        configure_resource(intersight, moid)

    module.exit_json(**intersight.result)


if __name__ == '__main__':
    main()
