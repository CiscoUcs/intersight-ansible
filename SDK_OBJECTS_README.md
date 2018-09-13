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

Authentication with the Intersight API requires that use of API keys that should be generated within the Intersight UI.  See (https://intersight.com/help) or (https://communities.cisco.com/docs/DOC-76947) for more information on generating and using API keys.
If you do not have an Intersight account, you can create one and claim devices in Intersight using the DevNet Intersight Sandbox at https://devnetsandbox.cisco.com/RM/Diagram/Index/a63216d2-e891-4856-9f27-309ca61ec862?diagramType=Topology
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

localhost (the Ansible controller) can be used without the need to specify any hosts or inventory.  Hosts can also be specified to perform parallel actions.  A complete example of HyperFlex Edge Cluster deployment is provided through the following files in this repository:
```
inventory - specifies the groups and specific hosts used to deploy multiple HX Edge Clusters
group_vars/all - HX policy variables common to all HX Clusters
host_vars/sjc07-r13-hx-edge-[1234] - Host specific variables used for each cluster.  Note that Ansible does not actually interact with different host endpoints, but using hosts and host_vars allows for configuration of multiple clusters in parallel.
hx_policies.yml - Playbook for HX policy configuration
hx_cluster_profiles.yml - Playbook for HX cluster profile configuration
hx_assign_and_validate.yml - Playbook for HX server assignment to a profile and validate action.
hx_deploy.yml - Playbook for HX cluster deployment.
```
You will need to cusomtize the group_vars and host_vars files with your API key information and with server/policy/profile settings for your HX Edge environment.

Here are example command lines for running the hx_policies.yml and hx_cluster_profiles.yml playbooks to configure HyperFlex policies and cluster profiles:
```
ansible-playbook -i inventory hx_policies.yml
ansible-playbook -i inventory hx_cluster_profiles.yml
```

# Community:

* We are on Slack - slack requires registration, but the ucspython team is open invitation to
  anyone to register [here](https://ucspython.herokuapp.com)
