# -- scripts/deploy.sh - Main deployment script --
#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
ENVIRONMENT=${1:-dev}
PROJECT_ROOT=$(pwd)
PROJECT_SCRIPTS_ROOT="$PROJECT_ROOT/scripts"
ANSIBLE_DIR="$PROJECT_SCRIPTS_ROOT/ansible"

echo -e "${GREEN}=== Deploying App + UI to ECS Fargate ===${NC}"
echo -e "==== ${YELLOW}Environment: $ENVIRONMENT${NC} ====="

# Validate environment
if [ ! -f "$ANSIBLE_DIR/vars/${ENVIRONMENT}.yml" ]; then
    echo -e "${RED}Error: Environment file $ANSIBLE_DIR/vars/${ENVIRONMENT}.yml not found${NC}"
    exit 1
fi

# Run Ansible deployment
cd $ANSIBLE_DIR

echo -e "${YELLOW}Running Ansible deployment...${NC}"
ansible-playbook -i inventory/hosts deploy.yml \
    -e deployment_env=$ENVIRONMENT \
    -v

echo -e "${GREEN}Deployment completed!${NC}"