# region
aws_region = "us-east-1"
project_name = "med-counseling-cd"
environment = "dev"
aws_account_id = 381213352543
app_image = "381213352543.dkr.ecr.us-east-1.amazonaws.com/med-counseling-cd-app:latest"
ui_image = "381213352543.dkr.ecr.us-east-1.amazonaws.com/med-counseling-cd-ui:latest"
app_container_name = "med-counseling-cd-app"
ui_container_name = "med-counseling-cd-ui"

# ECS cluster name
# ecs_cluster_name = "med-counseling-cd"

# Fargate Task Definition Configuration
# app_image = "med-counseling-cd-app:latest" - Input as a variable
app_container_port = 8000
ui_container_port = 8501
cpu_units = 2048 # 256 (.25 vCPU), 512 (.5 vCPU), 1024 (1 vCPU), etc.
memory_mib = 4096 # 512MB, 1024MB, 2048MB, etc.
operating_system_family = "LINUX"
cpu_architecture = "ARM64"

# ECS Service Configuration
service_name = "med-counseling-cd-svc"
desired_count = 1 # Number of tasks to run
# health_check_path = "/"


# Networking (VPC and Subnets) - Below will be newly generated 
# vpc_id = "vpc-0abcdef1234567890" # Replace with your VPC ID
# private_subnet_ids = [
#   "subnet-0abcdef1234567890",
#   "subnet-0fedcba9876543210"
# ]

# Below apply to EC2
# project_name = "med-counseling-cd"
# instance_type = "t3.medium"
# key_pair_name = "??" # Replace with your own AWS key pair name