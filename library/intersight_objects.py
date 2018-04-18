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
module: intersight_objects
short_description: Configures API Objects on Cisco Intersight
description:
- Configures API Objects on Cisco Intersight.
- The Python SDK module, Python class within the module, and all properties must be directly specified.
- More information on the Intersight Python SDK and how to directly configure API Objects is available at
  U(https://github.com/CiscoUcs/intersight-python).
- For more information on Intersight see U(https://intersight.com/help).
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
  objects:
    description:
    - 'List of API objects to configure.  Each object must have the following:'
    - '- api_module: Name of the Python SDK module implementing the required API class.'
    - '- api_class: Name of the Python class that will be used to configure the object.'
    - '- api_method_prefix: Prefix used by all the POST/GET/PATCH/DELETE methods.  Common method suffixes for each operation will be appended by this module.'
    - '- get_filter: Query filter string used to check for an existing object whose properties match the desired object.'
    - '- data_module: Name of the Python SDK module used to interpret response data.'
    - '- data_class: Name of the Python class used to interpret reponse data.'
    - '- api_body: Properties used to configure the object.  See the Intersight API documentation for information on properties for each object type.'
    - Either objects or json_config_file must be specified.
  json_config_file:
    description:
    - 'Filename (absolute path) of a JSON configuration file.  The JSON file should have the same fields described in the objects option.'
    - Either objects or json_config_file must be specified.
requirements:
- intersight
author:
- David Soper (@dsoper2)
- CiscoUcs (@CiscoUcs)
version_added: '2.6'
'''

EXAMPLES = r'''
- name: Configure BIOS Policy with Hyper-Threading disabled
  intersight_objects:
    api_private_key: /Users/guest/Downloads/SecretKey.txt
    api_key_id: 596cc79e5d91b400010d15ad/596cc7945d91b400010d154e/5abbe2a67a78667776c127e0
    objects:
    - {
        "api_module": "intersight.apis.bios_policy_api",
        "api_class": "BiosPolicyApi",
        "api_method_prefix": "bios_policies",
        "get_filter": "Name eq 'ht-disable'",
        "data_module": "intersight.models.bios_policy",
        "data_class": "BiosPolicy",
        "api_body": {
            "Name": "ht-disable",
            "Processor": {
                "IntelHyperThreadingTech": "disabled",
                "BootPerformanceMode": "platform-default",
                "CmciEnable": "platform-default",
                "CoreMultiProcessing": "platform-default",
                "CpuEnergyPerformance": "platform-default",
                "EnhancedIntelSpeedStepTech": "platform-default",
                "ExecuteDisableBit": "platform-default",
                "ExtendedApic": "platform-default",
                "HwpmEnable": "platform-default",
                "ImcInterleave": "platform-default",
                "IntelTurboBoostTech": "platform-default",
                "IntelVirtualizationTechnology": "platform-default",
                "KtiPrefetch": "platform-default",
                "LlcPrefetch": "platform-default",
                "PackageCstateLimit": "platform-default",
                "ProcessorC1e": "platform-default",
                "ProcessorC6report": "platform-default",
                "PstateCoordType": "platform-default",
                "PwrPerfTuning": "platform-default",
                "Snc": "platform-default",
                "WorkLoadConfig": "platform-default",
                "XptPrefetch": "platform-default"
            }
        }
      }

- name: Remove BIOS Policy
  intersight_objects:
    api_private_key: /Users/guest/Downloads/SecretKey.txt
    api_key_id: 596cc79e5d91b400010d15ad/596cc7945d91b400010d154e/5abbe2a67a78667776c127e0
    objects:
    - {
        "api_module": "intersight.apis.bios_policy_api",
        "api_class": "BiosPolicyApi",
        "api_method_prefix": "bios_policies",
        "get_filter": "Name eq 'ht-disable'",
      }
    state: absent

- name: Configure BIOS Policy using a JSON configuration file
  intersight_objects:
    api_private_key: /Users/guest/Downloads/SecretKey.txt
    api_key_id: 596cc79e5d91b400010d15ad/596cc7945d91b400010d154e/5abbe2a67a78667776c127e0
    json_config_file: /Users/guest/Downloads/bios_policy_ht_disable.json
'''

RETURN = r'''
api_response:
  description: API response as a dictionary.
  returned: success
  type: dict
  sample: {
    "moid": "5ac2970d396e337134f65422
  }
'''

from importlib import import_module
import json
from ansible.module_utils.basic import AnsibleModule

# six is required by intersight so all imports are grouped below
try:
    from six import iteritems
    from intersight.intersight_api_client import IntersightApiClient
    from intersight.api_client import ApiClient
    HAS_INTERSIGHT = True
except ImportError:
    HAS_INTERSIGHT = False


def get_object(api_object, item):
    '''GET an object or list of objects using the passed in item parameters.  Always returns the 1st object if a list of objects is returned'''
    if item.get('get_filter'):
        kwargs = dict(filter=item['get_filter'])
    else:
        kwargs = {}

    if item.get('object_moid'):
        api_moid_get_method = getattr(api_object, item['api_method_prefix'] + '_moid_get')
        api_response = api_moid_get_method(item['object_moid'], **kwargs)
    else:
        api_get_method = getattr(api_object, item['api_method_prefix'] + '_get')
        api_response = api_get_method(**kwargs)

    response_dict = api_response.to_dict()
    if response_dict.get('results'):
        # get the 1st results object if a list was returned
        response_dict = response_dict['results'][0]

    return response_dict


def compare_values(expected, actual):
    try:
        for (key, value) in iteritems(expected):
            if not compare_values(value, actual[key]):
                return False
        else:
            # loop complete with all items matching
            return True
    except AttributeError,TypeError:
        if expected and actual != expected:
            return False
        else:
            return True


def main():
    argument_spec = dict(
        api_private_key=dict(type='path', required=True),
        api_uri=dict(type='str', default='https://intersight.com/api/v1'),
        api_key_id=dict(type='str', required=True),
        objects=dict(type='list'),
        json_config_file=dict(type='path'),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_one_of=[
            ['objects', 'json_config_file'],
        ],
        mutually_exclusive=[
            ['objects', 'json_config_file'],
        ],
    )

    if not HAS_INTERSIGHT:
        module.fail_json(msg='intersight module is not available')

    api_instance = IntersightApiClient(
        host=module.params['api_uri'],
        private_key=module.params['api_private_key'],
        api_key_id=module.params['api_key_id'],
    )

    err = False
    # note that all objects specified in the object list report a single result (including a single changed).
    result = dict(changed=False)
    try:
        if module.params.get('objects'):
            objects = module.params['objects']
        else:
            # either objects or json_config_file will be specified, so if there is no objects option use a config file
            with open(module.params['json_config_file']) as f:
                objects = json.load(f)

        for item in objects:
            moid = None
            props_match = False

            # import the module and GET the resource based on an optional filter param
            api_module = import_module(item['api_module'])

            api_class = getattr(api_module, item['api_class'])
            api_object = api_class(api_instance)
            response_dict = get_object(api_object, item)
            result['api_response'] = response_dict
            if response_dict.get('moid'):
                moid = response_dict['moid']

            if module.params['state'] == 'absent':
                # object must exist, but all properties do not have to match
                if moid:
                    if not module.check_mode:
                        api_moid_delete_method = getattr(api_object, item['api_method_prefix'] + '_moid_delete')
                        api_moid_delete_method(moid)
                    result['api_response'] = {}
                    result['changed'] = True
            else:
                # configure as present.  Note that no api_body implies a GET only - api_response from above returned
                if item.get('api_body'):
                    # configure based on api_body
                    if moid:
                        # check object properties
                        data_module = import_module(item['data_module'])

                        data_class = getattr(data_module, item['data_class'])
                        deserialize_instance = ApiClient()
                        data_object = deserialize_instance._ApiClient__deserialize_model(item['api_body'], data_class)
                        deserialize_dict = data_object.to_dict()
                        props_match = compare_values(deserialize_dict, response_dict)

                    if not props_match:
                        if not module.check_mode:
                            if moid:
                                # update the resource - user has to specify all the props they want updated
                                api_moid_patch_method = getattr(api_object, item['api_method_prefix'] + '_moid_patch')
                                api_response = api_moid_patch_method(moid, item['api_body'])
                            else:
                                # create the resource
                                api_post_method = getattr(api_object, item['api_method_prefix'] + '_post')
                                api_response = api_post_method(item['api_body'])

                            if not api_response:
                                result['api_response'] = get_object(api_object, item)
                        result['changed'] = True

    except Exception as e:
        err = True
        result['msg'] = "setup error: %s " % str(e)

    if err:
        module.fail_json(**result)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
