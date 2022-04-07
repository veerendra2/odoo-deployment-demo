#!/usr/bin/env bash
VAGRANT_VAGRANTFILE=Vagrantfile-nginx vagrant destroy
VAGRANT_VAGRANTFILE=Vagrantfile-postgresql vagrant destroy
kubectl delete -f k8s/prometheus/
kubectl delete -f k8s/odoo-configmap.yaml
kubectl delete -f k8s/odoo-deployment.yaml
minikube stop