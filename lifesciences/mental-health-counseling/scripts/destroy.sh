# -- scripts/destroy.sh - Cleanup script --
#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ENVIRONMENT=${1:-dev}
PROJECT_ROOT=$(pwd)
TERRAFORM_DIR="$PROJECT_ROOT/terraform"

echo -e "${YELLOW}Destroying infrastructure for environment: $ENVIRONMENT${NC}"

read -p "Are you sure you want to destroy all resources? (yes/no): " confirm

if [[ $confirm != "yes" ]]; then
    echo -e "${YELLOW}Destruction cancelled${NC}"
    exit 0
fi

cd $TERRAFORM_DIR

# Load variables
if [ -f "terraform.tfvars" ]; then
    source terraform.tfvars
else
    echo -e "${RED}Error: terraform.tfvars not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Destroying Terraform resources...${NC}"
terraform destroy -auto-approve \
    -var="aws_region=$aws_region" \
    -var="project_name=$project_name" \
    -var="environment=$ENVIRONMENT" \
    -var="app_image=dummy" \
    -var="ui_image=dummy"

echo -e "${GREEN}Infrastructure destroyed successfully${NC}"
