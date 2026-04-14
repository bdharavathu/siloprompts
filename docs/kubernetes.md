# Kubernetes and Helm

## Quick Install

```bash
helm install siloprompts ./helm/siloprompts
```

Open via port-forward:

```bash
kubectl port-forward svc/siloprompts 5002:5000
```

Open [http://localhost:5002](http://localhost:5002)

---

## Helm Configuration

See `helm/siloprompts/values.yaml` for all options. Key settings:

```yaml
replicaCount: 2

image:
  repository: bdharavathu/siloprompts
  tag: "latest"

config:
  port: 5000
  promptsDir: /app/prompts
  dataDir: /app/data

persistence:
  prompts:
    enabled: true
    accessMode: ReadWriteOnce
    size: 500Mi
  data:
    enabled: true
    accessMode: ReadWriteOnce
    size: 1Gi

ingress:
  enabled: false
  className: "nginx"
  hosts:
    - host: siloprompts.local
      paths:
        - path: /
          pathType: Prefix
```

### Upgrade

```bash
helm upgrade siloprompts ./helm/siloprompts --set image.tag=1.0.4
```

### Uninstall

```bash
helm uninstall siloprompts
```

---

## Team Adoption

SiloPrompts is built for personal use — no auth, no accounts, no friction. But small teams can adapt it by deploying on Kubernetes with an external SSO proxy for identity and a sidecar for bidirectional sync.

The key: an SSO proxy (OAuth2 Proxy, Authelia, etc.) handles authentication externally and passes a user header to SiloPrompts. A sidecar container syncs prompts between the local volume and the source of truth (Git or S3). SiloPrompts itself has zero auth code and zero sync code — it just reads and writes the filesystem.

### Architecture

```
User → SSO Proxy → X-Forwarded-User header → SiloPrompts → reads/writes PV
                                                                ↕
                                              Sidecar syncs PV ↔ S3/Git
```

1. **SSO proxy** authenticates users and sets `X-Forwarded-User` header
2. **SiloPrompts** reads the header for favorites, audit logging, and user context
3. Users browse, search, copy, create, edit, and favorite prompts through the UI
4. **Sidecar container** syncs the PV with the source of truth (Git or S3) bidirectionally

---

### Use Case 1: Git Backend with ArgoCD

Prompts live in a Git repository. A sidecar commits and pushes UI changes back to Git.

**Flow:**
```
User edits via UI → SiloPrompts writes to PV → Sidecar commits & pushes to Git
                                                       ↕
Team member pushes via CLI/PR → Git updated → Sidecar pulls to PV
```

**Helm values with Git sidecar:**
```yaml
# values-git.yaml
replicaCount: 1

initContainers:
  - name: git-clone
    image: alpine/git
    command:
      - sh
      - -c
      - git clone https://${GIT_TOKEN}@github.com/yourteam/team-prompts.git /app/prompts
    env:
      - name: GIT_TOKEN
        valueFrom:
          secretKeyRef:
            name: git-credentials
            key: token
    volumeMounts:
      - name: prompts
        mountPath: /app/prompts

sidecarContainers:
  - name: git-sync
    image: alpine/git
    command:
      - sh
      - -c
      - |
        cd /app/prompts
        git config user.name "siloprompts-bot"
        git config user.email "bot@siloprompts"
        while true; do
          git add -A
          git diff --cached --quiet || git commit -m "sync: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
          git push origin main
          git pull --rebase origin main
          sleep 300
        done
    volumeMounts:
      - name: prompts
        mountPath: /app/prompts
    resources:
      requests:
        memory: 64Mi
        cpu: 50m

volumes:
  - name: prompts
    emptyDir: {}
```

**ArgoCD Application:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: siloprompts
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/yourteam/siloprompts-deploy.git
    targetRevision: main
    path: helm/siloprompts
    helm:
      valueFiles:
        - values-git.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

---

### Use Case 2: S3 Backend

Prompts live in an S3 bucket. A sidecar syncs bidirectionally — no pod restarts, no human intervention.

**Flow:**
```
User edits via UI → SiloPrompts writes to PV → Sidecar pushes to S3
                                                     ↕
Team member uploads via CLI/CI → S3 updated → Sidecar pulls to PV
```

**Helm values with S3 sidecar:**
```yaml
# values-s3.yaml
replicaCount: 1

sidecarContainers:
  - name: s3-sync
    image: amazon/aws-cli
    command:
      - sh
      - -c
      - |
        while true; do
          aws s3 sync /app/prompts/ s3://yourteam-siloprompts/prompts/
          aws s3 sync s3://yourteam-siloprompts/prompts/ /app/prompts/
          sleep 300
        done
    env:
      - name: AWS_ACCESS_KEY_ID
        valueFrom:
          secretKeyRef:
            name: aws-credentials
            key: access-key
      - name: AWS_SECRET_ACCESS_KEY
        valueFrom:
          secretKeyRef:
            name: aws-credentials
            key: secret-key
      - name: AWS_DEFAULT_REGION
        value: us-east-1
    volumeMounts:
      - name: prompts
        mountPath: /app/prompts
    resources:
      requests:
        memory: 64Mi
        cpu: 50m

volumes:
  - name: prompts
    emptyDir: {}
```

---

## Ingress

```yaml
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: prompts.internal.yourcompany.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: siloprompts-tls
      hosts:
        - prompts.internal.yourcompany.com
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Pod stuck in `Pending` | Check `kubectl describe pod` — image pull or secret issues |
| Prompts empty after deploy | Init container failed — check logs with `-c git-clone` or `-c s3-sync` |
| Sidecar not pushing | Check `kubectl logs <pod> -c git-sync` for auth errors |
| S3 access denied | Verify IAM credentials in the Kubernetes secret |
| Git merge conflicts | Sidecar uses `--rebase` — conflicts may need manual resolution |

---

## Tips for Team Use

- **Use tags consistently** — agree on a shared vocabulary so search works across the library
- **Keep prompts atomic** — one prompt per file, with variations as sections
- **Enable S3 versioning or Git history** — always have a rollback path
- **Favorites are per-user** — stored server-side keyed by SSO header (v1.1.0+)
