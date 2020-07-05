resource "aws_apigatewayv2_api" "lambda" {
  name          = "${var.lambda_function_name}_${var.stage}_gatewayv2"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id           = aws_apigatewayv2_api.lambda.id
  integration_type = "AWS_PROXY"

  connection_type           = "INTERNET"
  integration_method        = "POST"
  integration_uri           = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:$${stageVariables.lambdaFunctionName}/invocations"
}

resource "aws_apigatewayv2_route" "lambda" {
  api_id    = aws_apigatewayv2_api.lambda.id
  route_key = "$default"
}

resource "aws_apigatewayv2_stage" "lambda" {
  count = var.create_lambda_function && var.enable_api_gatewayv2 ? length(keys(local.dist_manifest)) : 0
  api_id = aws_apigatewayv2_api.lambda.id
  name   = keys(local.dist_manifest)[count.index]
  stage_variables = {
    lambdaFunctionName = "${var.lambda_function_name}_${keys(local.dist_manifest)[count.index]}"
  }
}

resource "aws_apigatewayv2_deployment" "lambda" {
  count = var.create_lambda_function && var.enable_api_gatewayv2 ? 1 : 0
  api_id      = aws_apigatewayv2_api.lambda.id

  lifecycle {
    create_before_destroy = true
  }
}
