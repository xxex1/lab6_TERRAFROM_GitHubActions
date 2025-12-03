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

variable "ssh_public_key" {
  description = "SSH public key for EC2 instance access"
  type        = string
  default     = ""
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
    from_port   = 5000
    to_port     = 5000
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

resource "aws_key_pair" "deployer" {
  key_name   = "flask-pawnshop-deployer-v2"
  public_key = var.ssh_public_key
}

resource "aws_instance" "webapp_instance" {
  ami           = "ami-0a6793a25df710b06"
  instance_type = "t3.micro"
  vpc_security_group_ids = [aws_security_group.web_app.id]
  key_name      = aws_key_pair.deployer.key_name

  user_data = <<-EOF
              #!/bin/bash
              set -e

              # Update system
              yum update -y

              # Install Python 3 and pip
              yum install -y python3 python3-pip git

              # Create app directory
              mkdir -p /opt/webapp
              cd /opt/webapp

              # Install Flask
              pip3 install flask

              # Create a simple systemd service
              cat > /etc/systemd/system/webapp.service <<EOL
              [Unit]
              Description=Flask Pawnshop Application
              After=network.target

              [Service]
              Type=simple
              User=ec2-user
              WorkingDirectory=/opt/webapp
              ExecStart=/usr/bin/python3 /opt/webapp/app.py
              Restart=always
              RestartSec=10

              [Install]
              WantedBy=multi-user.target
              EOL

              # Set proper permissions
              chown -R ec2-user:ec2-user /opt/webapp

              # Note: Application code will be deployed via GitHub Actions
              EOF

  user_data_replace_on_change = true

  tags = {
    Name = "webapp_instance"
  }
}


output "instance_public_ip" {
  value       = aws_instance.webapp_instance.public_ip
  description = "Public IP address of the EC2 instance"
  sensitive   = true
}
