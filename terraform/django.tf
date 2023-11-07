module "django" {
  source                 = "./modules/django"
  lambda_function_name   = "djambda"
  lambda_handler         = "djambda.lgi.application"
  stage                  = "dev"
  aws_region             = var.aws_region
  create_lambda_function = true
  default_from_email     = var.default_from_email
  enable_api_gatewayv2   = true
  db_password            = var.db_password
}
