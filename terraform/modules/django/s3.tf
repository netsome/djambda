module "s3_bucket_app" {
  source                 = "cloudposse/s3-bucket/aws"
  version                = "4.0.0"
  #source                 = "git::https://github.com/cloudposse/terraform-aws-s3-bucket.git?ref=tags/4.0.0"
  force_destroy          = true
  user_enabled           = true
  versioning_enabled     = true
  allowed_bucket_actions = ["s3:DeleteObject", "s3:GetObject", "s3:ListBucket", "s3:PutObject"]
  name                   = "app"
  stage                  = var.stage
  namespace              = var.lambda_function_name
}

data "aws_s3_objects" "dist" {
  bucket = module.s3_bucket_app.bucket_id
  prefix = "dist"
}

data "aws_s3_object" "manifest" {
  count = var.create_lambda_function ? 1 : 0
  bucket = module.s3_bucket_app.bucket_id
  key = "manifest.json"
}

locals {
  # jsondecode orders manifest
  dist_manifest = var.create_lambda_function ? jsondecode(data.aws_s3_object.manifest[0].body) : {}
}

module "staticfiles" {
  #source                   = "git::https://github.com/cloudposse/terraform-aws-cloudfront-s3-cdn.git?ref=tags/0.92.0"
  source                   = "cloudposse/cloudfront-s3-cdn/aws"
  version                  = "0.92.0"
  origin_force_destroy     = true
  namespace                = var.lambda_function_name
  stage                    = var.stage
  name                     = "static"
  cors_allowed_headers     = ["*"]
  cors_allowed_methods     = ["GET", "HEAD", "PUT"]
  cors_allowed_origins     = ["*"]
  cors_expose_headers      = ["ETag"]
  allow_ssl_requests_only  = false
}

module "s3_user_staticfiles" {
  source       = "cloudposse/iam-s3-user/aws"
  version      = "1.2.0"
  #source       = "git::https://github.com/cloudposse/terraform-aws-iam-s3-user.git?ref=tags/1.2.0"
  namespace    = var.lambda_function_name
  stage        = var.stage
  name         = "s3_user_staticfiles"
  s3_actions   = [
    "s3:PutObject",
    "s3:GetObjectAcl",
    "s3:GetObject",
    "s3:ListBucket",
    "s3:DeleteObject",
    "s3:PutObjectAcl"
  ]
  s3_resources = [
    "arn:aws:s3:::${module.staticfiles.s3_bucket}/*",
    "arn:aws:s3:::${module.staticfiles.s3_bucket}"
  ]
}
