variable "lambda_function_name" {}
variable "lambda_handler" {}
variable "lambda_runtime" { default = "python3.8" }
variable "create_lambda_provisioned_concurrency" { default = false }
variable "create_db_instance" { default = true }
variable "create_lambda_function" { default = false }
variable "aws_region" {}
variable "github_repository" { default = "" }
variable "stage" {}
variable "default_from_email" {}
variable "enable_s3_endpoint" {default = false}
variable "enable_dynamodb_endpoint" {default = false}
variable "enable_ses_endpoint" {default = false}
variable "enable_api_gateway" {default = false}
variable "enable_api_gatewayv2" {default = false}
variable "db_password" {}