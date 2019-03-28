# intersight-ansible
* Ansible Modules for Cisco Intersight.
* Apache License, Version 2.0 (the "License") 

## News

This repo represents the working copy of modules for Cisco Intersight that will submitted to Ansible in the future.  This repo can be used to provide Cisco Intersight modules before their inclusion in official Ansible releases.

There is currently not support for scripted install/uninstall to avoid collision with Ansible hosted modules and ongoing maintenance.  If you are running playbooks from the top-level directory of this repository (with library and module_utils subdirectories) you should not need any other setup to use the modules.

If needed, you can specfiy this repo as a library and module_utils location with env variables or command line options (e.g., ANSIBLE_LIBRARY=./library ansible-playbook ..).  Alternatively, your .ansible.cfg file can be updated to use this repo as the library path with the following:
```
[defaults]
library = <path to intersight-ansible clone>/library
module_utils = <path to intersight-ansible clone>/module_utils
```

### Current Development Status

| Configuration Category | Configuration Task | Module Name | Status (planned for Ansible 2.6, Proof of Concept, TBD |
| ---------------------- | ------------------ | ----------- | ------ |
| General purpose resource config | Any (with user provided data) | intersight_rest_api | Planned for 2.8 |

### Ansible Development Notes

Modules in development follow processes documented at http://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html.  The modules support ansible-doc, and when submitted to Ansible they must pass Ansible CI testing and have integration tests.

When developing modules in this repository, here are a few helpful commands to sanity check the code and documentation (replace module_name with your module (e.g., intersight_objects)).  Ansible modules won't generally be pylint or pycodestyle (PEP8) clean without disabling several of the checks:
  ```
  pylint --disable=invalid-name,no-member,too-many-nested-blocks,redefined-variable-type,too-many-statements,too-many-branches,broad-except,line-too-long,missing-docstring,wrong-import-position,too-many-locals <module_name>.py
  
  pycodestyle --max-line-length 160 --config /dev/null --ignore E402 <module_name>.py
  
  ansible-doc <module_name>
  ```

### install
- ansible must be installed
```
sudo pip install ansible
```
- clone this repository 
```
git clone https://github.com/ciscoucs/intersight-ansible
```

### usage

Authentication with the Intersight API requires that use of API keys that should be generated within the Intersight UI.  See (https://intersight.com/help) or (https://communities.cisco.com/docs/DOC-76947) for more information on generating and using API keys.
If you do not have an Intersight account, you can create one and claim devices in Intersight using the DevNet Intersight Sandbox at https://devnetsandbox.cisco.com/RM/Diagram/Index/a63216d2-e891-4856-9f27-309ca61ec862?diagramType=Topology
Because Intersight has a single API endpoint, minimal setup is required in playbooks or variables to access the API.  Here's an example playbook:
```
---
- hosts: localhost
  connection: local
  gather_facts: no
  tasks:
  - name: Configure Boot Policy
    intersight_rest_api:
      api_private_key: <path to your private key>
      api_key_id: <your public key id>
      resource_path: /boot/PrecisionPolicies
      api_body: {
```

localhost (the Ansible controller) can be used without the need to specify any hosts or inventory.  Hosts can also be specified to perform parallel actions.  An example of Server Firmware Update on multiple servers is provided by the rest_update_server.yml playbook:

You will need to provide your own inventory file and cusomtize any variables in the playbook with settings for your environment.  Here is an example inventory file with 2 servers identified by name as shown in the Intersight UI:
```
[servers]
C220-WZP21420X9E
C220M5-WZP21420XAQ
```
Here are example command lines for running the rest_boot_policy.yml and rest_update_server.yml playbooks to configure policies and servers in Intersight:
```
ansible-playbook -i inventory rest_boot_policy.yml
ansible-playbook -i inventory rest_update_server.yml
```

# Community:

* We are on Slack - slack requires registration, but the ucspython team is open invitation to
  anyone to register [here](https://ucspython.herokuapp.com)
