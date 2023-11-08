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

