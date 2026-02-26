
terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name   = var.name
  cidr   = var.vpc_cidr

  azs             = var.azs
  private_subnets = var.private_subnets
  enable_nat_gateway = false
  enable_dns_hostnames = true
  enable_dns_support   = true
}

resource "aws_security_group" "privatelink_sg" {
  name        = "${var.name}-privatelink-sg"
  description = "SG for Interface Endpoints"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Placeholder for Snowflake PrivateLink service name (obtain from Snowflake account)
variable "snowflake_vpce_service_name" {
  type        = string
  description = "Interface endpoint service name provided by Snowflake for PrivateLink"
}

resource "aws_vpc_endpoint" "snowflake" {
  vpc_id            = module.vpc.vpc_id
  service_name      = var.snowflake_vpce_service_name
  vpc_endpoint_type = "Interface"
  security_group_ids = [aws_security_group.privatelink_sg.id]
  subnet_ids        = module.vpc.private_subnets
  private_dns_enabled = false
  tags = { Name = "${var.name}-snowflake-pl" }
}
