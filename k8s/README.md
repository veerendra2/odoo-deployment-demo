# Odoo Frontend Deployment on Kubernetes

Since Odoo saves the session on the filesystem, I had to build Docker image contains `session_db` module which saves the sessions in a shared database

### How to build docker image and push?
```
$ docker build -t odoo-app .
$ docker tag odoo-app:latest veerendrav2/odoo-app:latest
$ docker login
# Login with credentials
$ docker push veerendrav2/odoo-app:latest
``` 
I have already built and pushed to my docker hub account(veerendrav2/odoo-app:latest)

### Deploy on K8s(minikube)
```
$ kubectl create -f odoo-configmap.yaml
$ kubectl create -f oddd-deployment.yml

# Get minikube cluster ip
$ minikube ip
192.168.99.100
```
Access app at [http://192.168.99.100:32242](http://192.168.99.100:32242)

**NOTE:** There is an automated script/playbook that automates above process(Except Docker image building)
