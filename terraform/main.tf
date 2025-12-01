terraform {
  required_version = ">=0.13.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

resource "aws_security_group" "web_app" {
  name        = "web_app"
  description = "Security group for Flask web application"
  # ingress - вхідний egress - вихідний
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web_app"
  }
}

resource "aws_instance" "webapp_instance" {
  ami           = "ami-0669b163befffbdfc"
  instance_type = "t3.micro"
  security_groups = ["web_app"]

  tags = {
    Name = "webapp_instance"
  }
}

# Output block - displays the public IP address after infrastructure deployment
# This information is shown after successful 'terraform apply'
output "instance_public_ip" {
  value       = aws_instance.webapp_instance.public_ip
  description = "Public IP address of the EC2 instance"
  sensitive   = true
}
