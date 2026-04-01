# Robot Diagnosis System - Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Application Deployment](#application-deployment)
5. [Monitoring Setup](#monitoring-setup)
6. [Rollback Procedures](#rollback-procedures)
7. [Troubleshooting](#troubleshooting)

## Overview

This guide provides step-by-step instructions for deploying the Robot Diagnosis System to AWS EKS using our automated CI/CD pipeline.

### Architecture Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS Cloud                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      VPC                                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │  Public     │  │  Private    │  │  Database   │     │   │
│  │  │  Subnets    │  │  Subnets    │  │  Subnets    │     │   │
│  │  │             │  │             │  │             │     │   │
│  │  │  ALB        │  │  EKS        │  │  RDS        │     │   │
│  │  │  NAT GW     │  │  (Pods)     │  │  ElastiCache│     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Required Tools
- AWS CLI (v2.0+)
- kubectl (v1.28+)
- Helm (v3.13+)
- Terraform (v1.5+)
- Docker

### AWS Permissions
Ensure your AWS user/role has the following permissions:
- AmazonEKSClusterPolicy
- AmazonEKSServicePolicy
- AmazonEKSWorkerNodePolicy
- AmazonEC2FullAccess
- AmazonRDSFullAccess
- AmazonElastiCacheFullAccess
- AmazonS3FullAccess
- IAMFullAccess

### Environment Variables
```bash
export AWS_REGION=ap-southeast-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export EKS_CLUSTER_NAME=robot-diagnosis-cluster
export ENVIRONMENT=production  # or staging, dev
```

## Infrastructure Setup

### 1. Terraform Infrastructure

#### Initialize Terraform
```bash
cd devops/terraform/aws
terraform init
```

#### Plan Infrastructure
```bash
terraform plan -var="environment=production" -out=tfplan
```

#### Apply Infrastructure
```bash
terraform apply tfplan
```

This will create:
- VPC with public/private subnets
- EKS cluster with managed node groups
- RDS MySQL database
- ElastiCache Redis cluster
- Application Load Balancer
- Security groups and IAM roles

### 2. Configure kubectl

```bash
aws eks update-kubeconfig \
  --name robot-diagnosis-cluster \
  --region ap-southeast-1
```

Verify connection:
```bash
kubectl get nodes
```

## Application Deployment

### 1. Install Required Helm Charts

#### Add Helm Repositories
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add jetstack https://charts.jetstack.io
helm repo add external-secrets https://charts.external-secrets.io
helm repo add elastic https://helm.elastic.co
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update
```

#### Install Ingress-NGINX
```bash
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.replicaCount=2 \
  --set controller.nodeSelector."workload"="general"
```

#### Install Cert-Manager
```bash
helm upgrade --install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

#### Install External Secrets
```bash
helm upgrade --install external-secrets external-secrets/external-secrets \
  --namespace external-secrets \
  --create-namespace
```

### 2. Deploy Application

#### Using Helm (Production)
```bash
helm upgrade --install robot-diagnosis-prod ./devops/helm/robot-diagnosis-app \
  --namespace production \
  --create-namespace \
  --set global.environment=production \
  --set backend.image.tag=v1.0.0 \
  --set frontend.image.tag=v1.0.0 \
  --set javaService.image.tag=v1.0.0 \
  --set ingress.host=robot-diagnosis.example.com \
  --set replicaCount=3 \
  --wait --timeout 10m
```

#### Using Helm (Staging)
```bash
helm upgrade --install robot-diagnosis-staging ./devops/helm/robot-diagnosis-app \
  --namespace staging \
  --create-namespace \
  --set global.environment=staging \
  --set backend.image.tag=latest \
  --set frontend.image.tag=latest \
  --set javaService.image.tag=latest \
  --set ingress.host=staging.robot-diagnosis.example.com \
  --set replicaCount=2 \
  --wait --timeout 10m
```

### 3. Verify Deployment

```bash
# Check pods
kubectl get pods -n production

# Check services
kubectl get svc -n production

# Check ingress
kubectl get ingress -n production

# Check HPA
kubectl get hpa -n production
```

## Monitoring Setup

### 1. Install Prometheus + Grafana

```bash
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f devops/monitoring/prometheus/prometheus-values.yaml \
  --wait --timeout 10m
```

Access Grafana:
```bash
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
# Open http://localhost:3000
# Default credentials: admin/admin
```

### 2. Install ELK Stack

```bash
# Elasticsearch
helm upgrade --install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --create-namespace \
  -f devops/monitoring/elk/elasticsearch-values.yaml

# Kibana
helm upgrade --install kibana elastic/kibana \
  --namespace logging \
  -f devops/monitoring/elk/kibana-values.yaml

# Fluentd
helm upgrade --install fluentd fluent/fluentd \
  --namespace logging \
  -f devops/monitoring/elk/fluentd-values.yaml
```

### 3. Install Falco (Runtime Security)

```bash
helm upgrade --install falco falcosecurity/falco \
  --namespace falco \
  --create-namespace \
  -f devops/monitoring/falco/falco-values.yaml
```

## Rollback Procedures

### Application Rollback

#### Rollback to Previous Version
```bash
# View revision history
helm history robot-diagnosis-prod -n production

# Rollback to specific revision
helm rollback robot-diagnosis-prod 3 -n production

# Verify rollback
kubectl rollout status deployment/backend -n production
```

#### Emergency Rollback Script
```bash
#!/bin/bash
# rollback.sh - Emergency rollback script

NAMESPACE=${1:-production}
REVISION=${2:-0}  # 0 means previous revision

echo "Rolling back deployment in namespace: $NAMESPACE"

# Rollback Helm release
helm rollback robot-diagnosis-prod $REVISION -n $NAMESPACE

# Wait for rollback to complete
kubectl rollout status deployment/backend -n $NAMESPACE --timeout=300s
kubectl rollout status deployment/frontend -n $NAMESPACE --timeout=300s
kubectl rollout status deployment/java-service -n $NAMESPACE --timeout=300s

echo "Rollback completed successfully"
```

### Database Rollback

#### RDS Point-in-Time Recovery
```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier robot-diagnosis-production-db \
  --target-db-instance-identifier robot-diagnosis-production-db-recovery \
  --restore-time 2024-01-01T00:00:00Z
```

## Troubleshooting

### Common Issues

#### 1. Pods Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n production

# Check logs
kubectl logs <pod-name> -n production --previous

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'
```

#### 2. High Memory/CPU Usage
```bash
# Check resource usage
kubectl top pods -n production

# Check node resources
kubectl top nodes

# Check HPA status
kubectl get hpa -n production
```

#### 3. Database Connection Issues
```bash
# Test database connectivity
kubectl run -it --rm debug --image=mysql:8.0 --restart=Never -- mysql -h <rds-endpoint> -u admin -p

# Check secrets
kubectl get secrets -n production
kubectl describe secret db-credentials -n production
```

#### 4. Ingress Issues
```bash
# Check ingress status
kubectl describe ingress -n production

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Test connectivity
curl -v https://robot-diagnosis.example.com/health
```

### Health Check Commands

```bash
# Application health
curl https://robot-diagnosis.example.com/actuator/health

# Database health
curl https://robot-diagnosis.example.com/actuator/health/db

# Redis health
curl https://robot-diagnosis.example.com/actuator/health/redis

# All metrics
curl https://robot-diagnosis.example.com/actuator/metrics
```

### Log Collection

```bash
# Collect all logs
kubectl logs -n production -l app.kubernetes.io/name=backend --all-containers > backend-logs.txt

# Follow logs in real-time
kubectl logs -n production -l app.kubernetes.io/name=backend -f

# Get logs from previous container instance
kubectl logs -n production <pod-name> --previous
```

### Performance Debugging

```bash
# Profile CPU usage
kubectl exec -it <pod-name> -n production -- py-spy top --pid 1

# Check network connections
kubectl exec -it <pod-name> -n production -- netstat -an

# Check file descriptors
kubectl exec -it <pod-name> -n production -- ls -la /proc/1/fd
```

## Maintenance

### Regular Maintenance Tasks

#### Weekly
- Review monitoring dashboards
- Check disk usage on EBS volumes
- Review security alerts from Falco

#### Monthly
- Rotate database credentials
- Review and update security groups
- Update base Docker images
- Review and optimize resource requests/limits

#### Quarterly
- Disaster recovery drill
- Security audit
- Cost optimization review
- Capacity planning

## Support

For deployment issues, contact:
- DevOps Team: devops@example.com
- On-call: +1-xxx-xxx-xxxx
- Slack: #deployments
