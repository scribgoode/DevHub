# Define AWS provider and set the region for resource provisioning
provider "aws" {
  region = "us-east-2"
}

# Create a Virtual Private Cloud to isolate the infrastructure
resource "aws_vpc" "default" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "ProjectPals_EC2_VPC"
  }
}

# Internet Gateway to allow internet access to the VPC
resource "aws_internet_gateway" "default" {
  vpc_id = aws_vpc.default.id
  tags = {
    Name = "ProjectPals_EC2_Internet_Gateway"
  }
}

# Route table for controlling traffic leaving the VPC
resource "aws_route_table" "default" {
  vpc_id = aws_vpc.default.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.default.id
  }
  tags = {
    Name = "ProjectPals_EC2_Route_Table"
  }
}

# Subnet within VPC for resource allocation, in availability zone us-east-2a
resource "aws_subnet" "subnet1" {
  vpc_id                  = aws_vpc.default.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = false
  availability_zone       = "us-east-2a"
  tags = {
    Name = "ProjectPals_EC2_Subnet_1"
  }
}

# Another subnet for redundancy, in availability zone us-east-2b
resource "aws_subnet" "subnet2" {
  vpc_id                  = aws_vpc.default.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = false
  availability_zone       = "us-east-2b"
  tags = {
    Name = "ProjectPals_EC2_Subnet_2"
  }
}

# Associate subnets with route table for internet access
resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.subnet1.id
  route_table_id = aws_route_table.default.id
}
resource "aws_route_table_association" "b" {
  subnet_id      = aws_subnet.subnet2.id
  route_table_id = aws_route_table.default.id
}



# Security group for EC2 instance
resource "aws_security_group" "ec2_sg" {
  vpc_id = aws_vpc.default.id
  ingress {
    from_port   = 22
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Only allow HTTPS traffic from everywhere
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "EC2_Security_Group"
  }
}

# Define variable for RDS password to avoid hardcoding secrets
variable "secret_key" {
  description = "The Secret Key for Django"
  type        = string
  sensitive   = true
}

# EC2 instance for the local web app
resource "aws_instance" "web" {
  ami                    = "ami-0eb9d6fc9fab44d24" # Amazon Linux
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.subnet1.id # Place this instance in one of the private subnets
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]

  associate_public_ip_address = true # Assigns a public IP address to your instance
  user_data_replace_on_change = true # Replace the user data when it changes

  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name

  user_data = <<-EOF
    #!/bin/bash
    set -ex
    yum update -y
    yum install -y yum-utils

    # Install Docker
    yum install -y docker
    service docker start

    # Install AWS CLI
    yum install -y aws-cli

    # Authenticate to ECR
    aws ecr get-login-password --region us-east-2 | docker login -u AWS --password-stdin 571600867484.dkr.ecr.us-east-2.amazonaws.com

    # Pull the Docker image from ECR
    docker pull 571600867484.dkr.ecr.us-east-2.amazonaws.com/projectpals-ec2:latest

    # Run the Docker image
    docker run -d -p 80:8080 \
    --env SECRET_KEY=${var.secret_key} \
    --env DB_NAME=projectpalsdb \
    --env DB_USER=projectpalsuser \
    --env DB_PASSWORD="SillyOnion42)" \
    --env DB_HOST=my-projectpals-rds.cn00esgis1oz.us-east-2.rds.amazonaws.com \
    --env DB_PORT=5432 \
    571600867484.dkr.ecr.us-east-2.amazonaws.com/projectpals-ec2:latest
    EOF

  tags = {
    Name = "ProjectPals_EC2_Complete_Server"
  }
}

# IAM role for EC2 instance to access ECR
resource "aws_iam_role" "ec2_role" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = {
        Service = "ec2.amazonaws.com",
      },
      Effect = "Allow",
    }],
  })
}

# Attach the AmazonEC2ContainerRegistryReadOnly policy to the role
resource "aws_iam_role_policy_attachment" "ecr_read" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# IAM instance profile for EC2 instance
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "projectpals_ec2_complete_profile"
  role = aws_iam_role.ec2_role.name
}