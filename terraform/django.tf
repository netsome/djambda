module "django" {
  source            = "./modules/django"
  lambda_function_name = "djambda"
  lambda_handler = "djambda.awsgi.lambda_handler"
  stage             = "dev"
  aws_region        = var.aws_region
  create_lambda_function = true
  default_from_email = var.default_from_email
}
