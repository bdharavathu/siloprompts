.PHONY: help build up down logs restart clean test test-live

# Configuration
CHART_NAME := siloprompts
NAMESPACE := siloprompts
RELEASE_NAME := siloprompts

# Default target
help:
	@echo "SiloPrompts Web Interface - Make Commands"
	@echo ""
	@echo "Docker Compose Commands:"
	@echo "  make build        - Build Docker image"
	@echo "  make up           - Start containers"
	@echo "  make down         - Stop containers"
	@echo "  make logs         - View logs"
	@echo "  make restart      - Restart containers"
	@echo "  make clean        - Remove containers and images"
	@echo "  make test         - Run pytest test suite"
	@echo "  make test-live    - Test live deployment"
	@echo ""
	@echo "Helm Commands:"
	@echo "  make helm-install    - Install chart with Helm"
	@echo "  make helm-upgrade    - Upgrade chart with Helm"
	@echo "  make helm-uninstall  - Uninstall chart"
	@echo "  make helm-status     - Show Helm release status"
	@echo "  make helm-lint       - Lint Helm chart"
	@echo "  make helm-template   - Render Helm templates"
	@echo "  make helm-package    - Package Helm chart"
	@echo ""
	@echo "Kubernetes Commands:"
	@echo "  make k8s-logs     - View Kubernetes logs"
	@echo "  make k8s-status   - Check Kubernetes status"
	@echo "  make k8s-port-forward - Port forward to localhost"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev          - Run in development mode"
	@echo "  make shell        - Open shell in container"

# Docker Compose Commands
build:
	@echo "Building Docker image..."
	docker-compose build

up:
	@echo "Starting SiloPrompts..."
	@mkdir -p ./data
	docker-compose up -d
	@echo "SiloPrompts is running at http://localhost:5000"

down:
	@echo "Stopping SiloPrompts..."
	docker-compose down

logs:
	docker-compose logs -f

restart: down up

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	docker rmi siloprompts:latest 2>/dev/null || true

test:
	pytest tests/ -v

test-live:
	@echo "Testing live deployment..."
	@curl -f http://localhost:5000/health && echo "✅ Health check passed" || echo "❌ Health check failed"
	@curl -f http://localhost:5000/api/categories && echo "✅ API working" || echo "❌ API failed"

# Helm Commands
helm-install:
	@echo "Installing $(CHART_NAME) with Helm..."
	helm install $(RELEASE_NAME) ./helm/$(CHART_NAME) -n $(NAMESPACE) --create-namespace
	@echo "Waiting for deployment..."
	kubectl wait --for=condition=available --timeout=60s deployment/$(RELEASE_NAME) -n $(NAMESPACE)

helm-upgrade:
	@echo "Upgrading $(RELEASE_NAME)..."
	helm upgrade $(RELEASE_NAME) ./helm/$(CHART_NAME) -n $(NAMESPACE)

helm-uninstall:
	@echo "Uninstalling $(RELEASE_NAME)..."
	helm uninstall $(RELEASE_NAME) -n $(NAMESPACE)

helm-status:
	helm status $(RELEASE_NAME) -n $(NAMESPACE)

helm-lint:
	@echo "Linting Helm chart..."
	helm lint ./helm/$(CHART_NAME)

helm-template:
	@echo "Rendering Helm templates..."
	helm template $(RELEASE_NAME) ./helm/$(CHART_NAME)

helm-package:
	@echo "Packaging Helm chart..."
	helm package ./helm/$(CHART_NAME)

helm-dry-run:
	@echo "Dry run installation..."
	helm install $(RELEASE_NAME) ./helm/$(CHART_NAME) -n $(NAMESPACE) --dry-run --debug

# Kubernetes Commands
k8s-logs:
	kubectl logs -f -n $(NAMESPACE) -l app.kubernetes.io/name=$(CHART_NAME)

k8s-status:
	@echo "Checking Kubernetes status..."
	kubectl get all -n $(NAMESPACE)

k8s-port-forward:
	@echo "Port forwarding to localhost:5002..."
	kubectl port-forward -n $(NAMESPACE) svc/$(RELEASE_NAME) 5002:80

# Development Commands
dev:
	@echo "Running in development mode..."
	FLASK_ENV=development python app.py

shell:
	docker-compose exec siloprompts /bin/sh

# Build and push to registry (for production)
push:
	@read -p "Enter registry URL (e.g., docker.io/username): " registry; \
	docker tag siloprompts:latest $$registry/siloprompts:latest; \
	docker push $$registry/siloprompts:latest
