# SiloPrompts Helm Chart

This Helm chart deploys SiloPrompts on Kubernetes with version management and easy configuration.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure (or use hostPath for local development)

## Installing the Chart

### Quick Install (Development)

```bash
# From the webapp directory
helm install siloprompts ./helm/siloprompts

# Or specify namespace
helm install siloprompts ./helm/siloprompts -n siloprompts --create-namespace
```

### Production Install with Custom Values

```bash
# Create a custom values file
cat > my-values.yaml <<EOF
replicaCount: 3

image:
  repository: your-registry/siloprompts
  tag: "1.0.0"

secret:
  secretKey: "your-production-secret-key-here"

persistence:
  data:
    hostPath:
      enabled: false
      path: ""
    storageClass: "your-storage-class"

ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: siloprompts.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: siloprompts-tls
      hosts:
        - siloprompts.yourdomain.com
EOF

# Install with custom values
helm install siloprompts ./helm/siloprompts -f my-values.yaml -n siloprompts --create-namespace
```

## Configuration

The following table lists the configurable parameters of the SiloPrompts chart and their default values.

### Application Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `2` |
| `image.repository` | Image repository | `siloprompts` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `config.flaskEnv` | Flask environment | `production` |
| `config.port` | Application port | `5000` |
| `secret.secretKey` | Secret key for Flask | `change-me-in-production` |

### Service Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `5000` |

### Ingress Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.hosts` | Ingress hosts | `[{host: siloprompts.local, paths: [{path: /, pathType: Prefix}]}]` |
| `ingress.tls` | TLS configuration | `[]` |

### Persistence Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `persistence.prompts.enabled` | Enable prompts PVC | `true` |
| `persistence.prompts.size` | Prompts PVC size | `500Mi` |
| `persistence.prompts.storageClass` | Storage class | `""` |
| `persistence.prompts.hostPath.enabled` | Use hostPath | `false` |
| `persistence.data.enabled` | Enable data PVC | `true` |
| `persistence.data.size` | Data PVC size | `1Gi` |
| `persistence.data.hostPath.enabled` | Use hostPath for data | `true` |
| `persistence.data.hostPath.path` | HostPath location | `/Users/bdharavathu/codespace/pvdata/silopromptsdata` |

### Resource Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |

### Autoscaling Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Enable HPA | `false` |
| `autoscaling.minReplicas` | Minimum replicas | `2` |
| `autoscaling.maxReplicas` | Maximum replicas | `10` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU % | `80` |

## Upgrading the Chart

```bash
# Upgrade with default values
helm upgrade siloprompts ./helm/siloprompts -n siloprompts

# Upgrade with custom values
helm upgrade siloprompts ./helm/siloprompts -f my-values.yaml -n siloprompts

# Upgrade with specific version
helm upgrade siloprompts ./helm/siloprompts --set image.tag=1.0.1 -n siloprompts
```

## Uninstalling the Chart

```bash
helm uninstall siloprompts -n siloprompts
```

## Examples

### Example 1: Local Development with HostPath

```yaml
# dev-values.yaml
replicaCount: 1

persistence:
  prompts:
    hostPath:
      enabled: true
      path: /path/to/your/prompts
  data:
    hostPath:
      enabled: true
      path: /path/to/data

resources:
  limits:
    cpu: 200m
    memory: 256Mi
```

```bash
helm install siloprompts ./helm/siloprompts -f dev-values.yaml
```

### Example 2: Production with LoadBalancer

```yaml
# prod-values.yaml
replicaCount: 3

image:
  repository: myregistry.io/siloprompts
  tag: "1.0.0"

secret:
  secretKey: "super-secret-production-key"

service:
  type: LoadBalancer

persistence:
  prompts:
    hostPath:
      enabled: false
    storageClass: "fast-ssd"
  data:
    hostPath:
      enabled: false
    storageClass: "standard"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

```bash
helm install siloprompts ./helm/siloprompts -f prod-values.yaml -n production --create-namespace
```

### Example 3: With Ingress and TLS

```yaml
# ingress-values.yaml
ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: siloprompts.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: siloprompts-tls
      hosts:
        - siloprompts.example.com
```

```bash
helm install siloprompts ./helm/siloprompts -f ingress-values.yaml -n siloprompts --create-namespace
```

## Helm Commands Cheat Sheet

```bash
# List all releases
helm list -n siloprompts

# Get release status
helm status siloprompts -n siloprompts

# Get release values
helm get values siloprompts -n siloprompts

# Get all release information
helm get all siloprompts -n siloprompts

# Rollback to previous version
helm rollback siloprompts -n siloprompts

# Rollback to specific revision
helm rollback siloprompts 1 -n siloprompts

# Show history
helm history siloprompts -n siloprompts

# Dry run (test without installing)
helm install siloprompts ./helm/siloprompts --dry-run --debug -n siloprompts

# Template (render templates locally)
helm template siloprompts ./helm/siloprompts

# Package the chart
helm package ./helm/siloprompts

# Lint the chart
helm lint ./helm/siloprompts
```

## Version Management

Helm provides built-in version management:

```bash
# Install version 1.0.0
helm install siloprompts ./helm/siloprompts --set image.tag=1.0.0 -n siloprompts

# Upgrade to 1.0.1
helm upgrade siloprompts ./helm/siloprompts --set image.tag=1.0.1 -n siloprompts

# Check history
helm history siloprompts -n siloprompts

# Rollback if needed
helm rollback siloprompts 1 -n siloprompts
```

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n siloprompts
kubectl describe pod <pod-name> -n siloprompts
kubectl logs <pod-name> -n siloprompts
```

### Check Service
```bash
kubectl get svc -n siloprompts
kubectl describe svc siloprompts -n siloprompts
```

### Check PVC
```bash
kubectl get pvc -n siloprompts
kubectl describe pvc siloprompts-data-pvc -n siloprompts
```

### Test Health Endpoint
```bash
kubectl port-forward svc/siloprompts 8080:80 -n siloprompts
curl http://localhost:8080/health
```

## Support

For issues or questions, please refer to the main documentation or open an issue in the repository.
