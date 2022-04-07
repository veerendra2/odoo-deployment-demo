# Odoo App Deployment

## Intro
Create a provisioning script to setup three servers with Odoo, two servers with PostgreSQL and two servers with Nginx. The PostgreSQL should be configured in replication mode (one main and one secondary). The three Odoo servers should run in Docker and use the PostgreSQL main server as the database. The two nginx servers should be configured as a reverse proxy to the three Odoo servers with caching of static files like JS, CSS files and images.


## Deployment
### Backend: Postgresql
`Vagrantfile-postgresql` is the Vagrant file to setup Postgresql DBs(Master and Slave). It uses `ansible` as provisioning tool to install and configure postgresql on both master and slave nodes by using ansible role `db`
* Deploys 2 VMs and configures in `master` `slave` replications
* Installs Prometheus `node_exporter` as systemd daemon. Can be scrap metrics on TCP port 9100 on both VM with their IPs

### Frontend: Odoo App
Odoo app is chosen to deploy as containers on K8s, unlike backend or proxies servers, this actual app is subjected to CI/CD i.e continuously apply changes/fixes. K8s container solution provides high velocity deployments.

In this deployment, I'm using `minikube` single node K8s cluster to deploy Odoo app. `minikube` uses `VirtualBox` to create single node K8s VM and generates `kubeconfig` on host.

* Created Docker image contains `session_db` module which saves the sessions in a shared database.(You can find more info at [k8s](https://gitlab.com/veerendrav2/odoo_deploy/tree/master/k8s) directory)
* Deploys 3 instances(Pods) of Odoo app
* Created [`odoo-configmap.yaml`](https://gitlab.com/veerendrav2/odoo_deploy/blob/master/k8s/odoo-configmap.yaml) configmap, useful to tweak Odoo app configuration if any
* Since minikube is only for dev purpose and can run only in local nodes, I have create `NodePort` 32242 to access app(`http://<cluster-ip>:<nodeport>`)
* Included Prometheus server and `cavisor` daemonset K8s deployment files to monitor app pods in K8s

### Proxies: Nginx Servers
`Vagrantfile-nginx` is the Vagrant file to setup Nginx servers. It uses `proxies` ansible role to install and configure nginx proxy 
* Deploys 2 VM - `nginx1` & `nginx2`
* Installs Prometheus `node_exporter` as systemd daemon. Can be scrap metrics on TCP port 9100 on both VM with their IPs
* Configures reverse proxy and cache for Odoo app

## Automation
`run.py` automates complete deployment flow and also does basic checks and verifications.

```
$ ./run.py 

** Odoo App deployment process consists of below steps **
1. Starts Minikube clsuter
2. Deploys Prometheus server on minikube
3. Starts Postgresql Master-Slave VMs
4. Deploys Odoo app on Minikube
5. Starts Nignx proxies VMs

Are you sure want to start deployment? [y/n] >y
...
```
##### Script in-action with [asciinema.org](https://asciinema.org)
[![demo](https://asciinema.org/a/271447.svg)](https://asciinema.org/a/271447?autoplay=1)

## Info
* More info on Ansible roles in [`provisioning`](https://gitlab.com/veerendrav2/odoo_deploy/tree/master/provisioning) directory
* More info on docker image building and app deployment in [`k8s`](https://gitlab.com/veerendrav2/odoo_deploy/tree/master/k8s) directory
* [`teardown.sh`](https://gitlab.com/veerendrav2/odoo_deploy/blob/master/teardown.sh) - Destroys complete deployment
* [`install_dep.sh`](https://gitlab.com/veerendrav2/odoo_deploy/blob/master/install_dep.sh) - Installs dependency packages

## Heads-Up :raised_hand:
* Vagrant setup uses default configuration of `Virtualbox` networking i.e  `host-only adapter` with subnet `192.168.99.0/24`
* `minikube` uses default configuration which launches VM on `host-only adapter`
* This deployment needs below packages, use `install_dep.sh` to install
  * Virtual Box
  * Vagrant
  * Ansible
  * Minikube
 
## Topology

### Virtual Box LAN Topology
```
              +-------------------------+
   +--------+-+       NAT/Internet      +------+
   |        | +---------+--------+------+      |
   |        |           |        |             |
   |        |           |        |             |
   |        |           |        |     +-------+---------+
+--+--+  +--+--+     +--+--+  +--+--+  |                 |
|     |  |     |     |     |  |     |  | Minikube Cluster|
| P1  |  | P2  |     | N1  |  | N2  |  |                 |
|     |  |     |     |     |  |     |  |                 |
+--+--+  +--+--+     +--+--+  +--+--+  |                 |
   |        |           |        |     +-------+---------+
   |        |           |        |             |
   |        |           |        |             |
   |        |  +--------+--------+------+      |
   +--------+--+  VirtualBox vboxnet1   +------+
               +------------------------+
```

### App Topology
```
     +--------+          +-------+
     |        |          |       |
     |        |     +----+ App   +---+
     |        |     |    |       |   |
+---->  N1    +-----+    +-------+   |
     |        |     |                |     +--------+    +--------+
     |        |     |    +-------+   |     |        |    |        |
     +--------+     |    |       |   |     |  P1    |    |  P2    |
                    +----+ App   |   |     |        |    |        |
     +--------+     |    |       |   +-----+        <---->        |
     |        |     |    +-------+   |     |        |    |        |
     |        |     |                |     |        |    |        |
     |        +-----+    +-------+   |     +--------+    +--------+
+---->  N2    |     |    |       |   |
     |        |     +----+ App   +---+
     |        |          |       |
     +--------+          +-------+

Legend:

P1 & P2 ==> Postgresql Master/Salve
N1 & N2 ==> Nginx Proxies
App     ==> Odoo App Deployed on K8s as containers
```
