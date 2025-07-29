
import subprocess
import sys

from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    # aws_ec2 as ec2,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr as ecr,
    App, Environment
)

REGION = "us-east-1"
USER_AWS_ACCOUNT = "381213352543"
APP_DOCKER_NAME = "med-counseling-app"
UI_DOCKER_NAME = "med-counseling-ui"

REGISTRY_URI = f"{USER_AWS_ACCOUNT}.dkr.ecr.{REGION}.amazonaws.com"

CLUSTER_NAME = "med-counseling-cd"
APP_REPOSITORY = "med-counseling-cd-app"
UI_REPOSITORY = "med-counseling-cd-ui"
TASK_SERVICE = "med-counseling-task-app-service"

class DockerDeploymentStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        # vpc = ec2.Vpc(self, "MyVpc", max_azs=2)

        # Create ECS Cluster
        cluster = ecs.Cluster(self, id=CLUSTER_NAME)
        # cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        # Create ECR Repository
        repository = ecr.Repository(self, id=APP_REPOSITORY, 
            repository_name=APP_REPOSITORY
        )

        # Create Fargate Service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, TASK_SERVICE,
            cluster=cluster,
            memory_limit_mib=2048,
            desired_count=2,
            cpu=1024,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(repository, "latest"),
                container_port=80
            )
        )

def build_and_push_image(docker_name, docker_file_path):
    """Build and push Docker image to ECR"""
    print("Building Docker image...")
    
    # Build image
    subprocess.run(["docker", "build", "--no-cache", "-f", docker_file_path, "-t", f"{docker_name}:latest", "."], check=True)
    
    # Get ECR login token
    result = subprocess.run([
        "aws", "ecr", "get-login-password", "--region", REGION
    ], capture_output=True, text=True, check=True)
    
    login_token = result.stdout.strip()
    
    # Login to ECR
    subprocess.run([
        "docker", "login", "--username", "AWS", "--password-stdin",
        REGISTRY_URI
    ], input=login_token, text=True, check=True)
    
    # Tag and push image
    ecr_uri = f"{REGISTRY_URI}/{docker_name}:latest"
    subprocess.run(["docker", "tag", f"{docker_name}:latest", ecr_uri], check=True)
    subprocess.run(["docker", "push", ecr_uri], check=True)
    
    print("Image pushed successfully!")




def deploy_stack():
    """Deploy CDK stack"""
    print("Deploying CDK stack...")
    
    app = App()
    DockerDeploymentStack(app, "DockerDeploymentStack",
        env=Environment(account=USER_AWS_ACCOUNT, region=REGION)
    )
    
    # Bootstrap CDK (if not already done)
    try:
        subprocess.run(["cdk", "bootstrap"], check=True)
    except subprocess.CalledProcessError:
        print("CDK bootstrap already completed or failed")
    
    # Deploy stack
    subprocess.run(["cdk", "deploy", "--require-approval", "never"], check=True)
    print("Stack deployed successfully!")


def main():
    """Main deployment function"""
    try:
        print("Starting AWS CDK deployment...")
        
        # App - Build and push Docker image
        build_and_push_image(APP_DOCKER_NAME, "app/Dockerfile")
        build_and_push_image(UI_DOCKER_NAME, "ui/Dockerfile")
        
        # Deploy CDK stack
        deploy_stack()
        
        print("Deployment completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Deployment failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()