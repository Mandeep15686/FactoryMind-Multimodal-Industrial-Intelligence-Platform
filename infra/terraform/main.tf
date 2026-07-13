terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }
  backend "s3" {
    bucket         = "factorymind-tf-state"
    key            = "factorymind/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "factorymind-tf-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type    = string
  default = "dev"
}

locals {
  name = "factorymind-${var.environment}"
  tags = {
    Project     = "FactoryMind"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

module "eks" {
  source      = "./modules/eks"
  name        = local.name
  environment = var.environment
  tags        = local.tags
}

module "rds" {
  source      = "./modules/rds"
  name        = local.name
  environment = var.environment
  tags        = local.tags
}

module "msk" {
  source      = "./modules/msk"
  name        = local.name
  environment = var.environment
  tags        = local.tags
}

module "elasticache" {
  source      = "./modules/elasticache"
  name        = local.name
  environment = var.environment
  tags        = local.tags
}

module "s3" {
  source      = "./modules/s3"
  name        = local.name
  environment = var.environment
  tags        = local.tags
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "rds_endpoint" {
  value = module.rds.endpoint
}
