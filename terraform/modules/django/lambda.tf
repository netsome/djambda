data "aws_iam_policy_document" "lambda" {
  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRole",
    ]

    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.lambda_function_name}_${var.stage}_role"
  assume_role_policy = data.aws_iam_policy_document.lambda.json
}

/* Define IAM permissions for the Lambda functions. */

data "aws_iam_policy_document" "lambda_basic_execution" {
  statement {
    sid = "AWSLambdaBasicExecutionRole"

    actions = [
      # AWSLambdaVPCAccessExecutionRole
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "lambda_basic_execution" {
  name   = "${var.lambda_function_name}_${var.stage}_policy"
  policy = data.aws_iam_policy_document.lambda_basic_execution.json
}

resource "aws_iam_role_policy_attachment" "attach_base_policy" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda_basic_execution.arn
}

data "aws_iam_policy_document" "ses" {
  count = var.enable_ses_endpoint ? 1 : 0
  statement {
    actions   = ["ses:SendRawEmail"]
    resources = ["*"]
    effect    = "Allow"
  }
}

resource "aws_iam_user" "ses" {
  count = var.enable_ses_endpoint ? 1 : 0
  name          = "ses"
}

# Defines a user that should be able to send send emails
resource "aws_iam_user_policy" "ses" {
  count = var.enable_ses_endpoint ? 1 : 0
  name   = aws_iam_user.ses[0].name
  user   = aws_iam_user.ses[0].name
  policy = data.aws_iam_policy_document.ses[0].json
}

# Generate API credentials
resource "aws_iam_access_key" "ses" {
  count = var.enable_ses_endpoint ? 1 : 0
  user  = aws_iam_user.ses[0].name
}

locals {
  ses_config = {
    enabled = {
      ENABLE_SMTP_EMAIL_BACKEND = "False"
      EMAIL_HOST = "email-smtp.${var.aws_region}.amazonaws.com"
      EMAIL_PORT = "587"
      EMAIL_HOST_USER = var.enable_ses_endpoint ? aws_iam_access_key.ses[0].id : ""
      EMAIL_HOST_PASSWORD = var.enable_ses_endpoint ? aws_iam_access_key.ses[0].ses_smtp_password_v4 : ""
      EMAIL_USE_TLS = "True"
      DEFAULT_FROM_EMAIL = var.default_from_email
    }
    disabled = {}
  }
}

resource "aws_lambda_function" "function" {
  count = var.create_lambda_function ? length(keys(local.dist_manifest)) : 0

  function_name = "${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}"
  handler = var.lambda_handler
  role    = aws_iam_role.lambda.arn
  runtime = var.lambda_runtime

  memory_size = 256
  timeout = 30

  s3_bucket = module.s3_bucket_app.bucket_id
  s3_key = values(local.dist_manifest)[count.index].file
  source_code_hash = values(local.dist_manifest)[count.index].filebase64sha256
  publish = true

  vpc_config {
    subnet_ids = module.vpc.private_subnets
    security_group_ids = [data.aws_security_group.default.id, module.postgresql_security_group.security_group_id]
  }

  environment {
    variables = merge(
      {
        ALLOWED_HOSTS = "*"
        DEBUG = "False"
        DATABASE_URL = "postgres://${module.db.db_instance_username}:${var.db_password}@${module.db.db_instance_address}:${module.db.db_instance_port}/${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}"
        FORCE_SCRIPT_NAME = "/${keys(local.dist_manifest)[count.index]}/"
        DJANGO_SUPERUSER_PASSWORD=random_password.password.result
        ENABLE_MANIFEST_STORAGE = "True"
        STATIC_URL = "https://${module.staticfiles.cf_domain_name}/${keys(local.dist_manifest)[count.index]}/"
        STATIC_ROOT = "/var/task/"
        LOGGING_LEVEL = "DEBUG"
      },
      local.ses_config[var.enable_ses_endpoint == true ? "enabled" : "disabled"]
    )
  }

  provisioner "local-exec" {
    when    = destroy
    command = "./script/invoke_dropdb.py ${self.function_name} ${self.function_name}"
    working_dir = path.module
  }
}

data "aws_lambda_invocation" "createdb" {
  count = length(keys(local.dist_manifest))
  function_name = "${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}"
  depends_on = [aws_lambda_function.function]

  input = jsonencode(
    {
      manage = ["createdb", "${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}", "--exist_ok"]
    }
  )
}

data "aws_lambda_invocation" "migrate" {
  count = length(keys(local.dist_manifest))
  function_name = "${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}"
  depends_on = [data.aws_lambda_invocation.createdb]

  input = jsonencode(
    {
      manage = ["migrate", "--noinput"]
    }
  )
}

resource "aws_lambda_permission" "apigw" {
  count = var.create_lambda_function && var.enable_api_gateway ? length(aws_lambda_function.function) : 0

  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function[count.index].function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.lambda.execution_arn}/*/*"
}

resource "aws_lambda_permission" "apigwv2" {
  count = var.create_lambda_function && var.enable_api_gatewayv2 ? length(aws_lambda_function.function) : 0

  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function[count.index].function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_apigatewayv2_api.lambda[0].execution_arn}/*/*"
}

resource "aws_lambda_provisioned_concurrency_config" "main" {
  count = var.create_lambda_provisioned_concurrency == "true" ? 1 : 0

  function_name                     = aws_lambda_function.function[0].function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.function[0].version
}
