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
module: intersight_facts
short_description: Gather facts about Intersight
description:
- Gathers facts about servers in L(Cisco Intersight,https://intersight.com).
extends_documentation_fragment: intersight
options:
  server_names:
    description:
    - Server names to retrieve facts from.  An empty list will return all servers.
    required: yes
author:
- David Soper (@dsoper2)
- CiscoUcs (@CiscoUcs)
version_added: '2.8'
'''

EXAMPLES = r'''
vars:
  api_info: &api_info
    api_private_key: <private key PEM file>
    api_key_id: <public key id>

# Gather facts for all servers
- intersight_facts:
    <<: *api_info
    server_names:
  delegate_to: localhost

# Gather facts for a list of servers
- intersight_facts:
    <<: *api_info
    server_names:
      - SJC18-L14-UCS1-1
      - SJC18-L14-UCS1-2
      - SJC18-L14-UCS1-3
      - SJC18-L14-UCS1-4
      - SJC18-L14-UCS1-5
      - SJC18-L14-UCS1-6
      - SJC18-L14-UCS1-7
      - SJC18-L14-UCS1-8
  delegate_to: localhost

# Gather facts for a single service given in the inventory
- intersight_facts:
    <<: *api_info
    server_names:
      - "{{ inventory_hostname }}"
  delegate_to: localhost
'''

from ansible.module_utils.remote_management.intersight import IntersightModule, intersight_argument_spec
from ansible.module_utils.basic import AnsibleModule


def get_servers(module, intersight):
    query_list = []
    if module.params['server_names']:
        for server in module.params['server_names']:
            query_list.append("Name eq '%s'" % server)
    query_str = ' or '.join(query_list)
    options = {
        'http_method': 'get',
        'resource_path': '/compute/PhysicalSummaries',
        'query_params': {
            '$filter': query_str,
        }
    }
    response_dict = intersight.call_api(**options)

    return response_dict.get('Results')


def main():
    argument_spec = intersight_argument_spec
    argument_spec.update(
        server_names=dict(type='list', required=True),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )

    intersight = IntersightModule(module)

    # one API call returning all requested servers
    module.exit_json(ansible_facts=dict(intersight_servers=get_servers(module, intersight)))


if __name__ == '__main__':
    main()
