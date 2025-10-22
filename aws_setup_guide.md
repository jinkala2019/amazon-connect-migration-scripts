# AWS Credentials Setup Guide

## Method 1: AWS CLI Configuration (Recommended)

```bash
# Install AWS CLI
pip install awscli

# Configure default credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format

# Or configure a named profile
aws configure --profile connect-migration
```

## Method 2: Environment Variables

```bash
# Windows (Command Prompt)
set AWS_ACCESS_KEY_ID=your-access-key
set AWS_SECRET_ACCESS_KEY=your-secret-key
set AWS_DEFAULT_REGION=us-east-1

# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_DEFAULT_REGION="us-east-1"

# Linux/Mac
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

## Method 3: IAM Role (EC2 only)

If running on EC2, attach an IAM role with Connect permissions.

## Usage Examples with Different Credential Methods

### Using Default Credentials
```bash
python connect_user_export.py --instance-id abc123 --region us-east-1
```

### Using Named Profile
```bash
python connect_user_export.py --instance-id abc123 --profile connect-migration
```

### Using Environment Variables
```bash
# Set environment variables first, then run
python connect_user_export.py --instance-id abc123
```

## Required IAM Permissions

Create an IAM user/role with this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "connect:ListUsers",
                "connect:DescribeUser",
                "connect:CreateUser",
                "connect:ListRoutingProfiles",
                "connect:DescribeRoutingProfile",
                "connect:CreateRoutingProfile",
                "connect:ListSecurityProfiles",
                "connect:DescribeSecurityProfile",
                "connect:ListUserHierarchyGroups",
                "connect:DescribeUserHierarchyGroup",
                "connect:ListQueues",
                "connect:DescribeQueue"
            ],
            "Resource": "*"
        }
    ]
}
```