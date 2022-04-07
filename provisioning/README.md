# Ansible Roles (Provisioner)

This directory contains ansible roles to install and configure servers. Below are the roles used in odoo app deployment
1. `common` - Generic configuration of server like DNS config and update
2. `db` - Installs and configures postgresql maser and slave VMs
3. `monitoring` - Sets up prometheus `node_exporter` for monitoring
4. `proxies` - Installs and configures nginx reserve proxy and cache VMs