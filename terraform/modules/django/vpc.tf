module "vpc_label" {
  source     = "git::https://github.com/cloudposse/terraform-null-label.git?ref=0.25.0"
  namespace  = var.lambda_function_name
  stage      = var.stage
  name       = "vpc"
}

module "sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 3.0"

  vpc_id = module.vpc.vpc_id
  name   = module.vpc_label.id

  egress_ipv6_cidr_blocks = []
  egress_cidr_blocks = []

  egress_prefix_list_ids = [module.vpc.vpc_endpoint_ses_id]

  tags = module.vpc_label.tags
}

data "aws_security_group" "default" {
  name   = "default"
  vpc_id = module.vpc.vpc_id
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "2.77.0"

  name = module.vpc_label.id

  cidr = "20.10.0.0/16"

  azs                 = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets     = ["20.10.1.0/24", "20.10.2.0/24", "20.10.3.0/24"]
  database_subnets    = ["20.10.21.0/24", "20.10.22.0/24", "20.10.23.0/24"]

  create_database_subnet_group = false

  enable_dns_hostnames = true
  enable_dns_support   = true

  # VPC endpoint for S3
  enable_s3_endpoint = var.enable_s3_endpoint

  # VPC endpoint for DynamoDB
  enable_dynamodb_endpoint = var.enable_dynamodb_endpoint

  # VPC endpoint for SES
  enable_ses_endpoint = var.enable_ses_endpoint
  ses_endpoint_private_dns_enabled = var.enable_ses_endpoint
  ses_endpoint_security_group_ids  = var.enable_ses_endpoint ? [data.aws_security_group.default.id] : []

  # VPC endpoint for SQS
  # enable_sqs_endpoint              = true
  # sqs_endpoint_private_dns_enabled = true
  # sqs_endpoint_security_group_ids  = [module.prod_sg.this_security_group_id]

  tags   = module.vpc_label.tags
}
