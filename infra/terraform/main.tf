terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source       = "./vpc"
  cluster_name = var.cluster_name
  environment  = var.environment
}

module "eks" {
  source       = "./eks"
  cluster_name = var.cluster_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnet_ids
}

module "s3" {
  source      = "./s3"
  environment = var.environment
}

module "sqs" {
  source      = "./sqs"
  environment = var.environment
}

module "iam" {
  source           = "./iam"
  environment      = var.environment
  cluster_name     = var.cluster_name
  oidc_provider    = module.eks.oidc_provider
  traces_bucket    = module.s3.traces_bucket_name
  results_bucket   = module.s3.results_bucket_name
  jobs_queue_arn   = module.sqs.jobs_queue_arn
}
