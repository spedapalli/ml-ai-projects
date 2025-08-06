# -- scripts/build.sh - Build and push Docker images --
#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
IMAGE_TAG=${IMAGE_TAG:-latest}

APP_NAME=${PROJECT_NAME:-'med-counseling-cd'}-app
UI_NAME=${PROJECT_NAME:-'med-counseling-cd'}-ui

echo -e "${GREEN}=== Building and Pushing Docker Images ===${NC}"

# Get ECR login token
echo -e "${YELLOW}Logging into ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push App image
echo -e "${YELLOW}Building App image...${NC}"
docker build -t $APP_NAME:$IMAGE_TAG apps/$APP_NAME/
docker tag $APP_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$APP_NAME:$IMAGE_TAG
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$APP_NAME:$IMAGE_TAG
echo -e "${GREEN}✓ App image pushed${NC}"

# Build and push Streamlit image
echo -e "${YELLOW}Building UI image...${NC}"
docker build -t $UI_NAME:$IMAGE_TAG apps/streamlit/
docker tag $UI_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$UI_NAME:$IMAGE_TAG
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$UI_NAME:$IMAGE_TAG
echo -e "${GREEN}✓ UI image pushed${NC}"

echo -e "${GREEN}All images built and pushed successfully!${NC}"