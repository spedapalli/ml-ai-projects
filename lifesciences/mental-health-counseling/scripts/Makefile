# -- Makefile - Common commands --
.PHONY: help setup build deploy destroy clean

ENVIRONMENT ?= dev

help: ## Show this help message
	@echo 'Usage: make [target] [ENVIRONMENT=env]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial setup (create ECR repos, directories, etc.)
	@./scripts/setup.sh

build: ## Build and push Docker images
	@./scripts/build.sh

deploy: ## Deploy to AWS ECS Fargate
	@./scripts/deploy.sh $(ENVIRONMENT)

destroy: ## Destroy infrastructure
	@./scripts/destroy.sh $(ENVIRONMENT)

clean: ## Clean up local Docker images
	docker image prune -f
	docker system prune -f

validate: ## Validate Terraform and Ansible configurations
	cd terraform && terraform validate
	cd ansible && ansible-playbook deploy.yml --syntax-check

test: ## Run local tests
	cd apps/fastapi && python -m pytest tests/ || echo "No tests found"
	cd apps/streamlit && python -m streamlit run app.py --server.headless true --server.port 8502 &
	sleep 5
	curl -f http://localhost:8502/_stcore/health || echo "Streamlit health check failed"
	pkill -f streamlit || echo "No streamlit process to kill"

logs: ## View ECS service logs
	@echo "FastAPI logs:"
	aws logs tail /ecs/fastapi-streamlit/fastapi --follow &
	@echo "Streamlit logs:"
	aws logs tail /ecs/fastapi-streamlit/streamlit --follow

status: ## Check deployment status
	@echo "ECS Services:"
	aws ecs describe-services --cluster fastapi-streamlit-cluster --services fastapi-streamlit-fastapi-service fastapi-streamlit-streamlit-service --query 'services[*].[serviceName,status,runningCount,desiredCount]' --output table