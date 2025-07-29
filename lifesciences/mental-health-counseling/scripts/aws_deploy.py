"""
AWS Docker Deployment Script for Mental Health Counseling. 
Deployed as 2 docker containers - App and UI
Deploys containers to AWS ECS with ECR, ALB, and VPC setup
"""

import boto3
import json
import time
import sys
from typing import Dict, Optional
import argparse
import subprocess
import json


class AWSDockerDeployer:

    REGION:str = "us-east-1"
    APP_DOCKER_NAME:str = "med-counseling-app"
    UI_DOCKER_NAME:str = "med-counseling-ui"
    CLUSTER_NAME:str = "med-counseling-cd"
    APP_REPOSITORY:str = "med-counseling-cd-app"
    UI_REPOSITORY:str = "med-counseling-cd-ui"
    APP_TASK:str = "med-counseling-cd-task-app"
    UI_TASK:str = "med-counseling-cd-task-ui"


    def __init__(self, region: str, cluster_name: str):
        self.region = region
        self.cluster_name = cluster_name
        
        # Initialize AWS clients
        self.ecs = boto3.client('ecs', region_name=region)
        self.ecr = boto3.client('ecr', region_name=region)
        self.ec2 = boto3.client('ec2', region_name=region)
        self.elbv2 = boto3.client('elbv2', region_name=region)
        self.iam = boto3.client('iam', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
        # self.elb = boto3.client('elbv2', region_name=region)
        
        self.account_id = boto3.client('sts').get_caller_identity()['Account']

    
        
    def _create_ecr_repositories(self, repos: list) -> Dict[str, str]:
        """Create ECR repositories for Docker images"""
        repo_uris = {}
        
        for repo_name in repos:
            try:
                response = self.ecr.create_repository(
                    repositoryName=repo_name,
                    imageScanningConfiguration={'scanOnPush': True}
                )
                repo_uri = response['repository']['repositoryUri']
                print(f"Created ECR repository: {repo_name}")
            except self.ecr.exceptions.RepositoryAlreadyExistsException:
                response = self.ecr.describe_repositories(repositoryNames=[repo_name])
                repo_uri = response['repositories'][0]['repositoryUri']
                print(f"ECR repository already exists: {repo_name}")
            
            repo_uris[repo_name] = repo_uri
            
        return repo_uris
    
    
    def _create_vpc_and_subnets(self) -> Dict[str, str]:
        """Create VPC with public and private subnets"""

        # If VPC already exists for the given name, return
        vpcs_existing = self.ec2.describe_vpcs(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [f'{self.cluster_name}-vpc']
                }
            ]
        )
        vpc = vpcs_existing.get('Vpcs', [])
        # get the VPC Id
        vpc_id = vpc[0]['VpcId']
        subnets = self.ec2.describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values':[vpc_id]}
            ]
        )
        # get the VPC subnets
        subnet_ids = [subnet['SubnetId'] for subnet in subnets['Subnets']]

        if vpc:
            print("++++++++++++++++++++ Returning existing VPC ++++++++++++++++++++")
            #TODO : Hard code to debug what object is returned
            return {
                'vpc_id': vpc_id, #'vpc-03391e36ad6c590ac',
                'subnet_ids': subnet_ids, # ['subnet-0a0e5aae628467d84', 'subnet-0277198dc6e67f726'], # subnet_ids,
            }


        # VPC does not exist. Create new
        vpc_response = self.ec2.create_vpc(CidrBlock='10.0.0.0/16')
        vpc_id = vpc_response['Vpc']['VpcId']
        
        # Wait for VPC to be available
        self.ec2.get_waiter('vpc_available').wait(VpcIds=[vpc_id])
        
        # Tag VPC
        self.ec2.create_tags(
            Resources=[vpc_id],
            Tags=[{'Key': 'Name', 'Value': f'{self.cluster_name}-vpc'}]
        )
        
        # Create Internet Gateway
        igw_response = self.ec2.create_internet_gateway()
        igw_id = igw_response['InternetGateway']['InternetGatewayId']
        
        # Attach Internet Gateway to VPC
        self.ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        
        # Get availability zones
        azs = self.ec2.describe_availability_zones()['AvailabilityZones'][:2]
        
        subnet_ids = []
        # Create public subnets
        for i, az in enumerate(azs):
            subnet_response = self.ec2.create_subnet(
                VpcId=vpc_id,
                CidrBlock=f'10.0.{i+1}.0/24',
                AvailabilityZone=az['ZoneName']
            )
            subnet_id = subnet_response['Subnet']['SubnetId']
            subnet_ids.append(subnet_id)
            
            # Tag subnet
            self.ec2.create_tags(
                Resources=[subnet_id],
                Tags=[{'Key': 'Name', 'Value': f'{self.cluster_name}-public-subnet-{i+1}'}]
            )
            
            # Enable auto-assign public IP
            self.ec2.modify_subnet_attribute(
                SubnetId=subnet_id,
                MapPublicIpOnLaunch={'Value': True}
            )
        
        # Create route table for public subnets
        rt_response = self.ec2.create_route_table(VpcId=vpc_id)
        route_table_id = rt_response['RouteTable']['RouteTableId']
        
        # Add route to Internet Gateway
        self.ec2.create_route(
            RouteTableId=route_table_id,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw_id
        )
        
        # Associate route table with subnets
        for subnet_id in subnet_ids:
            self.ec2.associate_route_table(
                RouteTableId=route_table_id,
                SubnetId=subnet_id
            )
        
        print(f"Created VPC: {vpc_id} with subnets: {subnet_ids}")
        
        return {
            'vpc_id': vpc_id,
            'subnet_ids': subnet_ids,
            'igw_id': igw_id
        }


    def _get_security_groups(self, vpc_id, sec_group_name:str) -> str:
        """Get a security group that matches given criteria of VPC Id and name. """
                # if Security Group already exists for the VPC Id, return
        try :
            alb_vpc_sec_groups = self.ec2.describe_security_groups(
                Filters=[
                    { 'Name': 'vpc-id', 'Values': [vpc_id]},
                    { 'Name': 'group-name', 'Values': [sec_group_name] }
                ]
            )

            if alb_vpc_sec_groups:
                return alb_vpc_sec_groups['SecurityGroups'][0]['GroupId']
        except Exception as e : 
            print(f"Security Groups do not exist for VPC Id {vpc_id} and Group name {sec_group_name}. Hence creating new.")
            return ''



    def _create_security_groups(self, vpc_id: str) -> Dict[str, str]:
        """Create security groups for ALB and ECS tasks"""

        alb_sec_grp_id = self._create_alb_security_groups(vpc_id)
        ecs_sec_grp_id = self._create_ecs_security_groups(vpc_id, alb_sec_grp_id)

        return {
            'alb_sg_id': alb_sec_grp_id,
            'ecs_sg_id': ecs_sec_grp_id
        }



    def _create_alb_security_groups(self, vpc_id:str) -> str:
        alb_sec_group_name = f'{self.cluster_name}-alb-secgrp'

        # if Security Group already exists for the VPC Id, return
        alb_sg_id = self._get_security_groups(vpc_id, alb_sec_group_name)

        if alb_sg_id : 
            print("++++++++++++++++++++ Returning the existing ALB security group ++++++++++++++++++++")
        else:
            # ALB Security Group -looks like EC2 APIs are needed to create the sec group for ALB
            alb_sg_response = self.ec2.create_security_group(
                GroupName= alb_sec_group_name,
                Description='Security group for Application Load Balancer',
                VpcId=vpc_id
            )
            alb_sg_id = alb_sg_response['GroupId']
            
            # Allow HTTP and HTTPS traffic to ALB
            self.ec2.authorize_security_group_ingress(
                GroupId=alb_sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 443,
                        'ToPort': 443,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )

        return alb_sg_id
        

    def _create_ecs_security_groups(self, vpc_id:str, alb_sec_group_id:str) -> str:
        # ECS Tasks Security Group
        ecs_sec_group_name = f'{self.cluster_name}-ecs-secgrp'

        ecs_sg_id = self._get_security_groups(vpc_id, ecs_sec_group_name)

        # If sec group does not exist, create one
        if ecs_sg_id:
            print("++++++++++++++++++++ Returning the existing ECS security group ++++++++++++++++++++")
        else:
            ecs_sg_response = self.ec2.create_security_group(
                GroupName= ecs_sec_group_name,
                Description='Security group for ECS tasks',
                VpcId=vpc_id
            )
            ecs_sg_id = ecs_sg_response['GroupId']
            
            # Allow traffic from ALB to ECS tasks
            self.ec2.authorize_security_group_ingress(
                GroupId=ecs_sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 8000,
                        'ToPort': 8000,
                        'UserIdGroupPairs': [{'GroupId': alb_sec_group_id}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 8501,
                        'ToPort': 8501,
                        'UserIdGroupPairs': [{'GroupId': alb_sec_group_id}]
                    }
                ]
            )
            
            print(f"Created security group for ECS: {ecs_sg_id}")
        
        return ecs_sg_id
        
    

    def _create_iam_roles(self) -> Dict[str, str]:
        """Create IAM roles for ECS tasks and execution"""
        # Task execution role
        execution_role_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            exec_role_response = self.iam.create_role(
                RoleName=f'{self.cluster_name}-execution-role',
                AssumeRolePolicyDocument=json.dumps(execution_role_doc),
                Description='ECS task execution role'
            )
            exec_role_arn = exec_role_response['Role']['Arn']
        except self.iam.exceptions.EntityAlreadyExistsException:
            exec_role_response = self.iam.get_role(RoleName=f'{self.cluster_name}-execution-role')
            exec_role_arn = exec_role_response['Role']['Arn']
        
        # Attach managed policy to execution role
        self.iam.attach_role_policy(
            RoleName=f'{self.cluster_name}-execution-role',
            PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'
        )
        
        # Task role (for application permissions)
        task_role_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            task_role_response = self.iam.create_role(
                RoleName=f'{self.cluster_name}-task-role',
                AssumeRolePolicyDocument=json.dumps(task_role_doc),
                Description='ECS task role'
            )
            task_role_arn = task_role_response['Role']['Arn']
        except self.iam.exceptions.EntityAlreadyExistsException:
            print(f"The IAM role {self.cluster_name}-task-role is already defined. Hence not creating a new one.")
            task_role_response = self.iam.get_role(RoleName=f'{self.cluster_name}-task-role')
            task_role_arn = task_role_response['Role']['Arn']
        
        print(f"Created IAM roles - Execution: {exec_role_arn}, Task: {task_role_arn}")
        
        return {
            'execution_role_arn': exec_role_arn,
            'task_role_arn': task_role_arn
        }
    

    def _create_cloudwatch_log_groups(self, services: list):
        """Create CloudWatch log groups for services"""
        for service in services:
            log_group_name = f'/ecs/{self.cluster_name}/{service}'
            try:
                self.logs.create_log_group(
                    logGroupName=log_group_name,
                )
                self.logs.put_retention_policy(
                    logGroupName=log_group_name,
                    retentionInDays=7
                )
                print(f"Created log group: {log_group_name}")
            except self.logs.exceptions.ResourceAlreadyExistsException:
                print(f"Log group already exists: {log_group_name}")

    
    def _create_ecs_cluster(self):
        """Create ECS cluster"""
        try:
            self.ecs.create_cluster(
                clusterName=self.cluster_name,
                capacityProviders=['FARGATE'],
                defaultCapacityProviderStrategy=[
                    {
                        'capacityProvider': 'FARGATE',
                        'weight': 1
                    }
                ]
            )
            print(f"Created ECS cluster: {self.cluster_name}")
        except self.ecs.exceptions.ClusterAlreadyExistsException:
            print(f"ECS cluster already exists: {self.cluster_name}")
    

    def _create_task_definition(self, service_name: str, image_uri: str, port: int, 
                             execution_role_arn: str, task_role_arn: str, 
                             env_values: Optional[dict] = None) -> str:
        """Create ECS task definition"""

        # Convert env vars into json string
        env_values_json:str = {}
        if env_values: 
            for key, value in env_values.items():
                env_values_json['name'] = key
                env_values_json['value'] = value

        # define the task
        task_def = {
            'family': service_name,
            'networkMode': 'awsvpc',
            'requiresCompatibilities': ['FARGATE'],
            'cpu': '2048',
            'memory': '8192',
            "runtimePlatform": {
                "cpuArchitecture": "ARM64",
                "operatingSystemFamily": "LINUX"
            },
            'executionRoleArn': execution_role_arn,
            'taskRoleArn': task_role_arn,
            'containerDefinitions': [
                {
                    'name': service_name,
                    'image': image_uri,
                    "cpu": 2048,
                    "memory": 8192,
                    'portMappings': [
                        {
                            'containerPort': port,
                            'protocol': 'tcp'
                        }
                    ],
                    'essential': True,
                    "environment": [
                        # json.dumps(env_values_json, indent=4)
                        env_values_json
                    ] if env_values_json else [],
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            'awslogs-group': f'/ecs/{self.cluster_name}/{service_name}',
                            'awslogs-region': self.region,
                            'awslogs-stream-prefix': 'ecs'
                        }
                    }
                }
            ]
        }
        
        response = self.ecs.register_task_definition(**task_def)
        task_def_arn = response['taskDefinition']['taskDefinitionArn']
        
        print(f"Created task definition for {service_name}: {task_def_arn}")
        return task_def_arn
    

    def _create_load_balancer(self, vpc_id:str, subnet_ids: list, alb_sg_id: str) -> Dict[str, str]:
        """Create Application Load Balancer"""
        # Create ALB - LB is part of EC2 and hence we use its APIs
        alb_response = self.elbv2.create_load_balancer(
            Name=f'{self.cluster_name}-alb',
            Subnets=subnet_ids,
            SecurityGroups=[alb_sg_id],
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4'
        )
        
        alb_arn = alb_response['LoadBalancers'][0]['LoadBalancerArn']
        alb_dns = alb_response['LoadBalancers'][0]['DNSName']
        
        # Create target groups
        app_tg_response = self.elbv2.create_target_group(
            Name=f'{self.cluster_name}-app-tg',
            Protocol='HTTP',
            Port=8000,
            VpcId=vpc_id, # subnet_ids[0].split('-')[0],  # Extract VPC ID from subnet
            TargetType='ip',
            HealthCheckPath='/docs'
        )
        
        ui_tg_response = self.elbv2.create_target_group(
            Name=f'{self.cluster_name}-ui-tg',
            Protocol='HTTP',
            Port=8501,
            VpcId=vpc_id, # subnet_ids[0].split('-')[0],  # Extract VPC ID from subnet
            TargetType='ip',
            HealthCheckPath='/'
        )
        
        app_tg_arn = app_tg_response['TargetGroups'][0]['TargetGroupArn']
        ui_tg_arn = ui_tg_response['TargetGroups'][0]['TargetGroupArn']
        
        # UI - Create listener
        self.elbv2.create_listener(
            LoadBalancerArn=alb_arn,
            Protocol='HTTP',
            Port=80,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': ui_tg_arn # app_tg_arn
                }
            ]
        )

        # App - Create Listener
        self.elbv2.create_listener(
            LoadBalancerArn=alb_arn,
            Protocol='HTTP',
            Port=8000,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': app_tg_arn
                }
            ]
        )
        
        print(f"Created ALB: {alb_dns}")
        
        return {
            'alb_arn': alb_arn,
            'alb_dns': alb_dns,
            'app_tg_arn': app_tg_arn,
            'ui_tg_arn': ui_tg_arn
        }
    

    def _create_ecs_service(self, service_name: str, task_def_arn: str, 
                          subnet_ids: list, ecs_sg_id: str, 
                          target_group_arn: str, public_ip: str, port: int):
        """Create ECS service"""
        
        service_config = {
            'cluster': self.cluster_name,
            'serviceName': f'{self.cluster_name}-{service_name}',
            'taskDefinition': task_def_arn,
            'desiredCount': 1,
            'launchType': 'FARGATE',
            'networkConfiguration': {
                'awsvpcConfiguration': {
                    'subnets': subnet_ids,
                    'securityGroups': [ecs_sg_id],
                    'assignPublicIp': public_ip # 'ENABLED' if service_name == 'ui' 'DISABLED'
                }
            },
            'loadBalancers': [
                {
                    'targetGroupArn': target_group_arn,
                    'containerName': service_name,
                    'containerPort': port # 8000 if service_name == 'app' else 8501
                }
            ]
        }
        
        self.ecs.create_service(**service_config)
        print(f"Created ECS service: {service_name}")
    


    def deploy_infrastructure(self, repo_uris: Dict[str, str]):

        """Deploy complete infrastructure"""
        print("Starting AWS infrastructure deployment...")
        
        # Create VPC and networking
        vpc_info = self._create_vpc_and_subnets()
        
        # Create security groups
        sg_info = self._create_security_groups(vpc_info['vpc_id'])
        
        # Create IAM roles
        iam_info = self._create_iam_roles()
        
        # Create CloudWatch log groups
        self._create_cloudwatch_log_groups([AWSDockerDeployer.APP_REPOSITORY, AWSDockerDeployer.UI_REPOSITORY])
        
        # Create ECS cluster
        self._create_ecs_cluster()
        
        # Wait a bit for IAM roles to propagate
        print("Waiting for IAM roles to propagate...")
        time.sleep(30)

        # Create task definitions
        app_task_arn = self._create_task_definition(
            AWSDockerDeployer.APP_TASK, 
            repo_uris['app'], 
            8000,
            iam_info['execution_role_arn'],
            iam_info['task_role_arn']
        )

        # create env vars
        #TODO : Below URL needs to be determined from the above app task definition
        ui_env_values: dict = {"API_URL": "http://3.93.163.25:8000"}

        ui_task_arn = self._create_task_definition(
            AWSDockerDeployer.UI_TASK, 
            repo_uris['ui'], 
            8501,
            iam_info['execution_role_arn'],
            iam_info['task_role_arn'], 
            ui_env_values
        )
        
        # Create load balancer
        alb_info = self._create_load_balancer(
            vpc_info['vpc_id'],
            vpc_info['subnet_ids'],
            sg_info['alb_sg_id']
        )
        
        # Create ECS services
        self._create_ecs_service(
            service_name=AWSDockerDeployer.APP_TASK,
            task_def_arn=app_task_arn,
            subnet_ids=vpc_info['subnet_ids'],
            ecs_sg_id=sg_info['ecs_sg_id'],
            target_group_arn=alb_info['app_tg_arn'], 
            public_ip='ENABLED',   # #TODO at some pt this backend UI shud be restricted to certain users only
            port=8000
        )
        
        self._create_ecs_service(
            service_name=AWSDockerDeployer.UI_TASK,
            task_def_arn=ui_task_arn,
            subnet_ids=vpc_info['subnet_ids'],
            ecs_sg_id=sg_info['ecs_sg_id'],
            target_group_arn=alb_info['app_tg_arn'],
            public_ip='ENABLED',
            port=8501
        )
        
        print(f"\nDeployment complete!")
        print(f"UI URL is at: http://{alb_info['alb_dns']}:8501")
        print(f"App URL (only to test backend APIs please) is : http://{alb_info['alb_dns']}")
        print(f"Note: Services may take a few minutes to become healthy")
        
        return {
            'alb_dns': alb_info['alb_dns'],
            'vpc_id': vpc_info['vpc_id'],
            'cluster_name': self.cluster_name
        }


    def _build_and_push_image(self, docker_name:str, docker_file_path:str, registry_uri: str, region:str):
        """Build and push Docker image to ECR"""
        print("Building Docker image...")
        
        # Build image
        subprocess.run(["docker", "build", "--no-cache", "-f", docker_file_path, "-t", f"{docker_name}:latest", "."], check=True)
        
        # Get ECR login token
        result = subprocess.run([
            "aws", "ecr", "get-login-password", "--region", region
        ], capture_output=True, text=True, check=True)
        
        login_token = result.stdout.strip()
        
        # Login to ECR
        subprocess.run([
            "docker", "login", "--username", "AWS", "--password-stdin",
            registry_uri
        ], input=login_token, text=True, check=True)
        
        # Tag and push image
        # ecr_uri = f"{registry_uri}/{docker_name}:latest"
        subprocess.run(["docker", "tag", f"{docker_name}:latest", registry_uri], check=True)
        subprocess.run(["docker", "push", registry_uri], check=True)
        
        print("Image pushed successfully!")


def main():
    parser = argparse.ArgumentParser(description='Deploy the Application and its UI to AWS')
    parser.add_argument('--region', default=AWSDockerDeployer.REGION, help='AWS region')
    parser.add_argument('--cluster-name', default=AWSDockerDeployer.CLUSTER_NAME, help='ECS cluster name')
    parser.add_argument('--app-image', help='Backend Docker image URI (optional)')
    parser.add_argument('--ui-image', help='Frontend(UI) Docker image URI (optional)')
    # parser.add_argument('--app-image', default=AWSDockerDeployer.APP_DOCKER_NAME, help='Backend Docker image URI (optional)')
    # parser.add_argument('--ui-image', default=AWSDockerDeployer.UI_DOCKER_NAME, help='Frontend(UI) Docker image URI (optional)')
    
    args = parser.parse_args()
    print(args)
    
    deployer = AWSDockerDeployer(args.region, args.cluster_name)
    
    # Create ECR repositories if images not provided
    repo_uris = {}
    if args.app_image:
        repo_uris['app'] = args.app_image
    if args.ui_image:
        repo_uris['ui'] = args.ui_image
    
    # Docker file location - Parametrize these ?
    app_docker_file = "./app/Dockerfile"
    ui_docker_file = "./ui/Dockerfile"
    
    # Create registries if user does not provide ECR in input
    if not repo_uris:
        print("Creating ECR repositories...")
        repo_uris = deployer._create_ecr_repositories([AWSDockerDeployer.APP_REPOSITORY, AWSDockerDeployer.UI_REPOSITORY])
        
        print("\nECR repositories created. Please build and push your Docker images:")
        for name, uri in repo_uris.items():
            print(f"\n{name.upper()} commands:")
            print(f"aws ecr get-login-password --region {args.region} | docker login --username AWS --password-stdin {uri}")
            print(f"docker build -t {name} .")
            print(f"docker tag {name}:latest {uri}:latest")
            print(f"docker push {uri}:latest")

            docker_file_path = app_docker_file if 'app' in name else ui_docker_file
            deployer._build_and_push_image(name, docker_file_path, uri, AWSDockerDeployer.REGION)
        
        # print(f"\nAfter pushing images, run this script again with:")
        # print(f"python {sys.argv[0]} --app-image {repo_uris['med-counseling-cd-app']}:latest --ui-image {repo_uris['med-counseling-cd-ui']}:latest")
        # return
    
    # Deploy infrastructure
    result = deployer.deploy_infrastructure(repo_uris)
    
    print(f"\n{'='*50}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'='*50}")
    print(f"Region: {args.region}")
    print(f"Cluster: {result['cluster_name']}")
    print(f"VPC ID: {result['vpc_id']}")
    print(f"Load Balancer DNS: {result['alb_dns']}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()


