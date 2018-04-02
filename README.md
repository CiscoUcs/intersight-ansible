# intersight-ansible
* Ansible Modules for Cisco Intersight.
* Apache License, Version 2.0 (the "License") 

## News

This repo represents the working copy of modules for Cisco Intersight that will submitted to Ansible in the future.  This repo can be used to provide Cisco Intersight modules before their inclusion in official Ansible releases.

There is currently not support for scripted install/uninstall to avoid collision with Ansible hosted modules and ongoing maintenance.  You can specfiy this repo as a library and module_utils location with env variables or command line options (e.g., ANSIBLE_LIBRARY=./library ansible-playbook ..).  Alternatively, your .ansible.cfg file can be updated to use this repo as the library path with the following:
```
[defaults]
library = <path to intersight-ansible clone>/library
```

### Current Development Status

| Configuration Category | Configuration Task | Module Name | Status (planned for Ansible 2.6, Proof of Concept, TBD |
| ---------------------- | ------------------ | ----------- | ------ |
| General purpose object config | Any (with user provided data) | intersight_objects | Planned for 2.6 |

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
- you will also need the Intersight Python SDK.
```
sudo pip install git+https://github.com/CiscoUcs/intersight-python.git
```
- clone this repository 
```
git clone https://github.com/ciscoucs/intersight-ansible
```
- Specfiy this repository as a library location in your .ansible.cfg file
```
[defaults]
library = <path to intersight-ansible clone>/library
```

### usage

Because Intersight has a single API endpoint, minimal setup is required in playbooks or variables to access the API.  Here's an example playbook:
```
---
- hosts: localhost
  connection: local
  gather_facts: no
  tasks:
  - name: Configure Server Profile
    intersight_objects:
      api_private_key: <path to your private key>
      api_key_id: <your public key id>
      objects:
      - {
        ...
```

Authentication with the Intersight API requires that use of API keys that should be generated within the Intersight UI.  See (https://intersight.com/help) for more information on generating and using API keys.

localhost (the Ansible controller) can be used without the need to specify any hosts or inventory.  Here's an example command line for running the example playbook in this repo to configure a Server Profile with a BIOS policy also configured:
```
ansible-playbook example_server_profile_with_bios_policy.yml
```

# Community:

* We are on Slack - slack requires registration, but the ucspython team is open invitation to
  anyone to register [here](https://ucspython.herokuapp.com)
