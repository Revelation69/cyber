#!/usr/bin/env python3
"""Render a reproducible CloudFormation template with embedded host scripts."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ref = lambda name: {"Ref": name}
sub = lambda value: {"Fn::Sub": value}
att = lambda name, field: {"Fn::GetAtt": [name, field]}
az = {"Fn::Select": [0, {"Fn::GetAZs": ""}]}
tags = [{"Key": "Project", "Value": "core1-simulator"}, {"Key": "Stack", "Value": ref("AWS::StackName")}]

def resource(kind, properties, **extra):
    return {"Type": kind, "Properties": properties, **extra}

def template():
    provider_arn = {"Fn::If": ["CreateProvider", ref("GitHubProvider"), ref("ExistingOidcProviderArn")]}
    bootstrap = (ROOT / "infra/bootstrap.sh").read_text()
    deploy = (ROOT / "infra/deploy.sh").read_text()
    user_data = [
        "#!/usr/bin/env bash\nset -Eeuo pipefail\nmkdir -p /etc/core1\n",
        "cat > /etc/core1/deploy.env <<'CONFIG'\nREGION=", ref("AWS::Region"),
        "\nREPOSITORY=", att("ImageRepository", "RepositoryUri"),
        "\nDOMAIN=", ref("DomainName"), "\nDATA_VOLUME=", ref("DataVolume"),
        "\nCADDY_IMAGE=caddy:2-alpine@sha256:6aeddd44c3078b0f9a35206472a11420648a79c184603ef95957d0a20044cb2b\nCONFIG\n",
        "chmod 600 /etc/core1/deploy.env\ncat > /usr/local/bin/core1-deploy <<'DEPLOY_SCRIPT'\n",
        deploy, "\nDEPLOY_SCRIPT\nchmod 700 /usr/local/bin/core1-deploy\n", bootstrap,
    ]
    resources = {
        "Vpc": resource("AWS::EC2::VPC", {"CidrBlock": "10.73.0.0/16", "EnableDnsSupport": True, "EnableDnsHostnames": True, "Tags": tags}),
        "InternetGateway": resource("AWS::EC2::InternetGateway", {"Tags": tags}),
        "GatewayAttachment": resource("AWS::EC2::VPCGatewayAttachment", {"VpcId": ref("Vpc"), "InternetGatewayId": ref("InternetGateway")}),
        "PublicSubnet": resource("AWS::EC2::Subnet", {"VpcId": ref("Vpc"), "CidrBlock": "10.73.1.0/24", "AvailabilityZone": az, "MapPublicIpOnLaunch": True, "Tags": tags}),
        "RouteTable": resource("AWS::EC2::RouteTable", {"VpcId": ref("Vpc"), "Tags": tags}),
        "PublicRoute": resource("AWS::EC2::Route", {"RouteTableId": ref("RouteTable"), "DestinationCidrBlock": "0.0.0.0/0", "GatewayId": ref("InternetGateway")}, DependsOn="GatewayAttachment"),
        "SubnetRoute": resource("AWS::EC2::SubnetRouteTableAssociation", {"SubnetId": ref("PublicSubnet"), "RouteTableId": ref("RouteTable")}),
        "WebSecurityGroup": resource("AWS::EC2::SecurityGroup", {"GroupDescription": "Core 1 web access; management uses SSM, no inbound SSH", "VpcId": ref("Vpc"), "SecurityGroupIngress": [{"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80, "CidrIp": ref("AllowedWebCidr")}], "Tags": tags}),
        "HttpsIngress": resource("AWS::EC2::SecurityGroupIngress", {"GroupId": ref("WebSecurityGroup"), "IpProtocol": "tcp", "FromPort": 443, "ToPort": 443, "CidrIp": ref("AllowedWebCidr")}, Condition="HasDomain"),
        "ImageRepository": resource("AWS::ECR::Repository", {"RepositoryName": sub("${AWS::StackName}-simulator"), "ImageTagMutability": "IMMUTABLE", "ImageScanningConfiguration": {"ScanOnPush": True}, "EncryptionConfiguration": {"EncryptionType": "AES256"}, "LifecyclePolicy": {"LifecyclePolicyText": json.dumps({"rules": [{"rulePriority": 1, "description": "Keep the latest twenty application images", "selection": {"tagStatus": "any", "countType": "imageCountMoreThan", "countNumber": 20}, "action": {"type": "expire"}}]})}, "Tags": tags}, DeletionPolicy="Retain", UpdateReplacePolicy="Retain"),
        "DataVolume": resource("AWS::EC2::Volume", {"AvailabilityZone": az, "Size": 8, "VolumeType": "gp3", "Encrypted": True, "Tags": tags}, DeletionPolicy="Retain", UpdateReplacePolicy="Retain"),
        "InstanceRole": resource("AWS::IAM::Role", {"AssumeRolePolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]}, "ManagedPolicyArns": [sub("arn:${AWS::Partition}:iam::aws:policy/AmazonSSMManagedInstanceCore")], "Policies": [{"PolicyName": "PullSimulatorImage", "PolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "ecr:GetAuthorizationToken", "Resource": "*"}, {"Effect": "Allow", "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer", "ecr:BatchCheckLayerAvailability"], "Resource": att("ImageRepository", "Arn")}]}}], "Tags": tags}),
        "InstanceProfile": resource("AWS::IAM::InstanceProfile", {"Roles": [ref("InstanceRole")]}),
        "Server": resource("AWS::EC2::Instance", {"ImageId": ref("AmiId"), "InstanceType": ref("InstanceType"), "AvailabilityZone": az, "SubnetId": ref("PublicSubnet"), "SecurityGroupIds": [ref("WebSecurityGroup")], "IamInstanceProfile": ref("InstanceProfile"), "MetadataOptions": {"HttpTokens": "required", "HttpEndpoint": "enabled", "HttpPutResponseHopLimit": 1}, "CreditSpecification": {"CPUCredits": "standard"}, "BlockDeviceMappings": [{"DeviceName": "/dev/xvda", "Ebs": {"VolumeSize": 8, "VolumeType": "gp3", "Encrypted": True, "DeleteOnTermination": True}}], "UserData": {"Fn::Base64": {"Fn::Join": ["", user_data]}}, "Tags": tags + [{"Key": "Name", "Value": sub("${AWS::StackName}-web")}]}, DependsOn=["PublicRoute", "SubnetRoute"]),
        "DataAttachment": resource("AWS::EC2::VolumeAttachment", {"Device": "/dev/sdf", "InstanceId": ref("Server"), "VolumeId": ref("DataVolume")}),
        "PublicIp": resource("AWS::EC2::EIP", {"Domain": "vpc", "Tags": tags}, DependsOn="GatewayAttachment"),
        "IpAttachment": resource("AWS::EC2::EIPAssociation", {"AllocationId": att("PublicIp", "AllocationId"), "InstanceId": ref("Server")}),
        "GitHubProvider": resource("AWS::IAM::OIDCProvider", {"Url": "https://token.actions.githubusercontent.com", "ClientIdList": ["sts.amazonaws.com"], "Tags": tags}, Condition="CreateProvider"),
        "DeployDocument": resource("AWS::SSM::Document", {"DocumentType": "Command", "DocumentFormat": "JSON", "UpdateMethod": "NewVersion", "Content": {"schemaVersion": "2.2", "description": "Deploy a verified ECR digest to the Core 1 host", "parameters": {"ImageDigest": {"type": "String", "interpolationType": "ENV_VAR", "allowedPattern": "^sha256:[0-9a-f]{64}$"}}, "mainSteps": [{"action": "aws:runShellScript", "name": "deploy", "inputs": {"timeoutSeconds": "600", "runCommand": ["set -eu", "test -f /etc/core1/bootstrap-complete", "/usr/local/bin/core1-deploy \"$SSM_ImageDigest\""]}}]}, "Tags": tags}),
    }
    resources["DeploymentRole"] = resource("AWS::IAM::Role", {
        "Description": "GitHub main branch may push only this app and run its fixed deployment document",
        "MaxSessionDuration": 3600,
        "AssumeRolePolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Federated": provider_arn}, "Action": "sts:AssumeRoleWithWebIdentity", "Condition": {"StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com", "token.actions.githubusercontent.com:sub": ref("GitHubOidcSubject")}}}]},
        "Policies": [{"PolicyName": "BuildAndDeploySimulator", "PolicyDocument": {"Version": "2012-10-17", "Statement": [
            {"Effect": "Allow", "Action": "ecr:GetAuthorizationToken", "Resource": "*"},
            {"Effect": "Allow", "Action": ["ecr:BatchGetImage", "ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload", "ecr:PutImage", "ecr:DescribeImages"], "Resource": att("ImageRepository", "Arn")},
            {"Effect": "Allow", "Action": "ssm:SendCommand", "Resource": [sub("arn:${AWS::Partition}:ssm:${AWS::Region}:${AWS::AccountId}:document/${DeployDocument}"), sub("arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:instance/${Server}")]},
            {"Effect": "Allow", "Action": "ssm:GetCommandInvocation", "Resource": "*"},
        ]}}], "Tags": tags,
    })
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Core 1 simulator: one small EC2 host, retained encrypted exam storage, ECR and GitHub OIDC deployment.",
        "Parameters": {
            "InstanceType": {"Type": "String", "Default": "t3.micro", "AllowedValues": ["t3.micro", "t3.small"]},
            "AmiId": {"Type": "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>", "Default": "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"},
            "DomainName": {"Type": "String", "Default": "", "AllowedPattern": "^$|^[a-z0-9][a-z0-9.-]*\\.[a-z]{2,}$", "Description": "Optional domain already pointed at this stack's Elastic IP; empty means HTTP public IP."},
            "AllowedWebCidr": {"Type": "String", "Default": "0.0.0.0/0", "AllowedPattern": "^[0-9.]+/[0-9]{1,2}$"},
            "ExistingOidcProviderArn": {"Type": "String", "Default": "", "AllowedPattern": "^$|^arn:aws:iam::[0-9]{12}:oidc-provider/token.actions.githubusercontent.com$"},
            "GitHubOidcSubject": {"Type": "String", "Default": "repo:Revelation69@97466660/cyber@1327682549:ref:refs/heads/main", "AllowedPattern": "^repo:[A-Za-z0-9_./@:-]+:ref:refs/heads/main$"},
        },
        "Conditions": {"CreateProvider": {"Fn::Equals": [ref("ExistingOidcProviderArn"), ""]}, "HasDomain": {"Fn::Not": [{"Fn::Equals": [ref("DomainName"), ""]}]}},
        "Resources": resources,
        "Outputs": {
            "InstanceId": {"Value": ref("Server")}, "PublicIp": {"Value": ref("PublicIp")},
            "AppUrl": {"Value": {"Fn::If": ["HasDomain", sub("https://${DomainName}"), sub("http://${PublicIp}")]}},
            "RepositoryUri": {"Value": att("ImageRepository", "RepositoryUri")},
            "DeploymentRoleArn": {"Value": att("DeploymentRole", "Arn")},
            "DeploymentDocument": {"Value": ref("DeployDocument")},
            "DataVolumeId": {"Value": ref("DataVolume")},
        },
    }

if __name__ == "__main__":
    output = ROOT / "infra/cloudformation.json"
    output.write_text(json.dumps(template(), indent=2) + "\n")
    print(output)
