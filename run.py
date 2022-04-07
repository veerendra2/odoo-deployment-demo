#!/usr/bin/env python2
'''
Author: Veerendra K
Description: Automation of deployment of oddo app
'''
import subprocess
import requests

WELCOME_BANNER = """
** Odoo App deployment process consists of below steps **
1. Starts Minikube clsuter
2. Deploys Prometheus server on minikube
3. Starts Postgresql Master-Slave VMs
4. Deploys Odoo app on Minikube
5. Starts Nignx proxies VMs
"""

SUCCESS_BANNER_DIAGRAM1 = """
## Physical LAN Connections ##

              +-------------------------+
   +--------+-+       NAT/Internet      +------+
   |        | +---------+--------+------+      |
   |        |           |        |             |
   |        |           |        |     +-------+---------+
+--+--+  +--+--+     +--+--+  +--+--+  |                 |
|     |  |     |     |     |  |     |  | Minikube Cluster|
| P1  |  | P2  |     | N1  |  | N2  |  |                 |
|     |  |     |     |     |  |     |  |                 |
+--+--+  +--+--+     +--+--+  +--+--+  |                 |
   |        |           |        |     +-------+---------+
   |        |           |        |             |
   |        |  +--------+--------+------+      |
   +--------+--+  VirtualBox vboxnet1   +------+
               +------------------------+
"""

SUCCESS_BANNER_DIAGRAM2 = """
### Virtual Connections ##

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
"""

LEGEND_BANNER = """
LEGEND
------
P1 & P2 ==> Postgresql Master/Salve
N1 & N2 ==> Nginx Proxies
App     ==> Odoo App Deployed on K8s as containers
"""

DETAILS_BANNER = """
** Access Links **
App Proxy 1: http://192.168.99.4
App Proxy 2: http://192.168.99.3
Prometheus Dashboard: http://{}:30900
"""


def execute(cmd, verbose=True):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = []
    while True:
        line = p.stdout.readline()
        out.append(line)
        if verbose:
            print line,
        if not line and p.poll() is not None:
            break
    if p.returncode != 0:
        print p.stderr.read().strip()
        return 1
    else:
        return ''.join(out).strip()


class deploy:
    def __init__(self):
        self.k8s_node_ip = None
        dependencies_cmds = ["ansible --version", "vagrant version",
                             "minikube version", "virtualbox --help"]
        print "[*] Running pre-flight checks"
        for cmd in dependencies_cmds:
            return_code = execute(cmd, verbose=False)
            if return_code == 1:
                print "[-] Not able to run '{}'. Please install dependency packages for deployment".format(cmd)
                exit(1)

    def start_minikube(self):
        print "[*] Starting minikube single node cluster"
        rt_code = execute("minikube start --vm-driver=virtualbox")
        if rt_code == 1:
            print "[*] Unable to start minikube"
            exit(1)
        cluster_ip = execute("minikube ip", verbose=False)
        if cluster_ip == 1:
            print "[*] Something went wrong. Unable to fetch minikube ip"
            exit(1)
        self.k8s_node_ip = cluster_ip
        print "[*] Writing cluster to var files"
        with open("provisioning/roles/proxies/vars/main.yml", "w") as f:
            f.write("cluster_ip: {}".format(cluster_ip))

    def deploy_odoo_app(self):
        print "[*] Deploying Odoo Application on K8s"
        execute("kubectl create -f k8s/odoo-configmap.yaml")
        execute("kubectl create -f k8s/odoo-deployment.yml")

    def deploy_prometheus_server(self):
        print "[*] Deploying Prometheus server in minikube"
        execute("kubectl create -f k8s/prometheus/")

    def deploy_postgresql(self):
        print "[*] Starting Postgresql VMs"
        code = execute("VAGRANT_VAGRANTFILE=Vagrantfile-postgresql vagrant up")
        if code == 1:
            print "[*] Unable to start Postgresql VMs"
            exit(1)

    def deploy_nginx(self):
        print "[*] Starting Nginx Proxies VMs"
        code = execute("VAGRANT_VAGRANTFILE=Vagrantfile-nginx vagrant up")
        if code == 1:
            print "[*] Unable to start Nginx Proxies VMs"
            exit(1)


if __name__ == '__main__':
    print WELCOME_BANNER
    res = raw_input("Are you sure want to start deployment? [y/n] >")
    if not res or res[0].capitalize() != "Y":
        print "[.] Aborted"
        exit()
    dep = deploy()
    dep.start_minikube()
    dep.deploy_prometheus_server()
    dep.deploy_postgresql()
    dep.deploy_odoo_app()
    dep.deploy_nginx()
    print SUCCESS_BANNER_DIAGRAM1
    print SUCCESS_BANNER_DIAGRAM2
    print LEGEND_BANNER
    print DETAILS_BANNER





