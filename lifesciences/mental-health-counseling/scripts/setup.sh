# -- setup.sh - Initial setup script --

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
PROJECT_NAME=${PROJECT_NAME:-med-counseling-cd}
ENVIRONMENT=${ENVIRONMENT:-dev}

echo -e "${GREEN}Setting up Mental Health Counseling App + UI deployment environment...${NC}"

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    commands=("aws" "terraform" "ansible" "docker")
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}Error: $cmd is not installed${NC}"
            exit 1
        else
            echo -e "${GREEN}✓ $cmd is installed${NC}"
        fi
    done
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}Error: AWS credentials are not configured${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ AWS credentials are configured${NC}"
    fi
}

# Create ECR repositories
create_ecr_repositories() {
    echo -e "${YELLOW}Creating ECR repositories...${NC}"
    
    repositories=("med-counseling-cd-app" "med-counseling-cd-ui")
    
    for repo in "${repositories[@]}"; do
        if aws ecr describe-repositories --repository-names $repo --region $AWS_REGION &> /dev/null; then
            echo -e "${GREEN}✓ ECR repository $repo already exists${NC}"
        else
            aws ecr create-repository --repository-name $repo --region $AWS_REGION > /dev/null
            echo -e "${GREEN}✓ Created ECR repository $repo${NC}"
        fi
    done
}

# Create S3 bucket for Terraform state (optional)
create_terraform_state_bucket() {
    BUCKET_NAME="${PROJECT_NAME}-terraform-state-${ENVIRONMENT}-$(date +%s)"
    
    read -p "Do you want to create an S3 bucket for Terraform remote state? (y/n): " create_bucket
    
    if [[ $create_bucket == "y" || $create_bucket == "Y" ]]; then
        echo -e "${YELLOW}Creating S3 bucket for Terraform state...${NC}"
        
        aws s3 mb s3://$BUCKET_NAME --region $AWS_REGION
        
        # Enable versioning
        aws s3api put-bucket-versioning --bucket $BUCKET_NAME --versioning-configuration Status=Enabled
        
        # Enable encryption
        aws s3api put-bucket-encryption --bucket $BUCKET_NAME --server-side-encryption-configuration '{
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }
            ]
        }'
        
        echo -e "${GREEN}✓ Created S3 bucket: $BUCKET_NAME${NC}"
        echo -e "${YELLOW}Update terraform_state_bucket in vars/${ENVIRONMENT}.yml with: $BUCKET_NAME${NC}"
    fi
}

# Create directory structure
create_directory_structure() {
    echo -e "${YELLOW}Creating directory structure...${NC}"
    
    directories=(
        "terraform"
        "ansible/vars"
        "ansible/tasks"
        "ansible/inventory"
        "apps/app"
        "apps/ui"
        "scripts"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p $dir
        echo -e "${GREEN}✓ Created directory: $dir${NC}"
    done
}

# Get AWS Account ID
get_aws_account_id() {
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo -e "${GREEN}AWS Account ID: $AWS_ACCOUNT_ID${NC}"
    
    # Update configuration files with AWS Account ID
    if [ -f "ansible/vars/${ENVIRONMENT}.yml" ]; then
        sed -i.bak "s/123456789012/$AWS_ACCOUNT_ID/g" "ansible/vars/${ENVIRONMENT}.yml"
        echo -e "${GREEN}✓ Updated AWS Account ID in ansible/vars/${ENVIRONMENT}.yml${NC}"
    fi
}

# Main setup function
main() {
    echo -e "${GREEN}=== Mental Health Counseling App + UI ECS Deployment Setup ===${NC}"
    
    check_prerequisites
    create_directory_structure
    create_ecr_repositories
    get_aws_account_id
    create_terraform_state_bucket
    
    echo -e "${GREEN}"
    echo "=========================================="
    echo "Setup completed successfully!"
    echo "=========================================="
    echo -e "${NC}"
    echo "Next steps:"
    echo "1. Review and update configuration files in ansible/vars/"
    echo "2. Build and deploy with: ./scripts/deploy.sh"
    echo "3. Access your applications via the Load Balancer URL"
}

main "$@"