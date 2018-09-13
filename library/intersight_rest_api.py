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
- For more information see L(Intersight,https://intersight.com/help).
options:
  api_private_key:
    description:
    - 'Filename (absolute path) of a PEM formatted file that contains your private key to be used for Intersight API authentication.'
    required: yes
  api_uri:
    description:
    - URI used to access the Intersight API.
    default: https://intersight.com/api/v1
  api_key_id:
    description:
    - Public API Key ID associated with the private key.
    required: yes
author:
- David Soper (@dsoper2)
- CiscoUcs (@CiscoUcs)
version_added: '2.6'
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
try:
    import ansible.module_utils.remote_management.intersight_rest as intersight
    HAS_INTERSIGHT = True
except ImportError:
    HAS_INTERSIGHT = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems


def call_api(module, result, **options):
    try:
        api_response = intersight.intersight_call(**options)
        if not re.match(r'2..', str(api_response.status_code)):
            raise RuntimeError(api_response.status_code, api_response.text)
    except Exception as e:
        result['msg'] = "API error: %s " % str(e)
        module.fail_json(**result)

    return api_response


def get_api_result(api_response):
    response_dict = api_response.json()
    if response_dict.get('Results'):
        # return the 1st list element
        response_dict = response_dict['Results'][0]

    return response_dict


def get_resource(module, result):
    options = {
        'http_method': 'get',
        'resource_path': module.params['resource_path'],
        'query_params': module.params['query_params'],
    }
    return get_api_result(call_api(module, result, **options))


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


def configure_resource(module, result, moid):
    if not module.check_mode:
        if moid:
            # update the resource - user has to specify all the props they want updated
            options = {
                'http_method': 'patch',
                'resource_path': module.params['resource_path'],
                'body': module.params['api_body'],
                'moid': moid,
            }
            result['api_response'] = get_api_result(call_api(module, result, **options))
        else:
            # create the resource
            options = {
                'http_method': 'post',
                'resource_path': module.params['resource_path'],
                'body': module.params['api_body'],
            }
            call_api(module, result, **options)
            result['api_response'] = get_resource(module, result)
    result['changed'] = True


def delete_resource(module, result, moid):
    # delete resource and create empty api_response
    if not module.check_mode:
        options = {
            'http_method': 'delete',
            'resource_path': module.params['resource_path'],
            'moid': moid,
        }
        call_api(module, result, **options)
        result['api_response'] = {}
    result['changed'] = True


def main():
    argument_spec = dict(
        api_private_key=dict(type='path', required=True),
        api_uri=dict(type='str', default='https://intersight.com/api/v1'),
        api_key_id=dict(type='str', required=True),
        resource_path=dict(type='str', required=True),
        query_params=dict(type='dict', default={}),
        api_body=dict(type='dict', default={}),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )

    if not HAS_INTERSIGHT:
        module.fail_json(msg='intersight_rest module is not available')

    intersight.set_private_key(open(module.params['api_private_key'], 'r').read())
    intersight.set_public_key(module.params['api_key_id'])

    result = dict(changed=False)
    result['api_response'] = {}

    # get the current state of the resource
    result['api_response'] = get_resource(module, result)

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
    if (request_config or request_delete) and result['api_response'].get('Moid'):
        # resource exists and moid was returned
        moid = result['api_response']['Moid']
        if request_config:
            resource_values_match = compare_values(module.params['api_body'], result['api_response'])
        else:  # request_delete
            delete_resource(module, result, moid)

    if request_config and not resource_values_match:
        configure_resource(module, result, moid)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
