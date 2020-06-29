# Djambda

Djambda is an example project setting up Django application in AWS Lambda managed by Terraform.

GitHub Actions create environments for [master branch](https://vp9x9htxm7.execute-api.eu-central-1.amazonaws.com/0/admin/) and [pull requests](https://vp9x9htxm7.execute-api.eu-central-1.amazonaws.com/1/admin/).

## Setup

### Github auth
* [Generate a personal access token](https://github.com/settings/tokens/new) in github. Check out the [docs](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line) in case you need help. Remember to check `repo` ([repository public key](https://developer.github.com/v3/actions/secrets/#get-a-repository-public-key)) and `workflow` scopes.
* Create organization in github. As of time of writing terraform doesn't support setting secrets in individual user account. This may change when [this](https://github.com/terraform-providers/terraform-provider-github/pull/465) pr gets upstreamed.

### Terraform Cloud
* [Create a workspace](https://www.terraform.io/docs/cloud/getting-started/workspaces.html#creating-a-workspace).
* [Edit variables](https://www.terraform.io/docs/cloud/getting-started/workspaces.html#editing-variables):
  * Terraform Variables:
    * `aws_region`
    * `github_repository`
  * Environment Variables:
    * `AWS_ACCESS_KEY_ID`
    * `AWS_SECRET_ACCESS_KEY`
    * `GITHUB_TOKEN`
    * `GITHUB_ORGANIZATION`
* Create [Terraform Cloud user API token](https://app.terraform.io/app/settings/tokens). You will need this later when setting up github repository.

### Github repository
* Fork this repo.
* Set `create_lambda_function` input in django module (`terraform/django.tf`) to `false`. This will prevent terraform from creating lambda related resources before building application.
* Set `organization` and `workspaces` in `terraform/main.tf`.
* Set `TF_API_TOKEN` repository secret.
* Re-run jobs.
* Set `create_lambda_function` input in django module (`terraform/django.tf`) to `true`.
* Re-run jobs.

## AWS resources

Terraform sets up following AWS resources:
* VPC with optional [endpoints](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-endpoints.html)
* Lambda with REST API Gateway
* RDS for PostgreSQL
* S3 bucket for static files behind CloudFront

## Related Projects
* [Zappa](https://github.com/Miserlou/Zappa)
* [chalice](https://github.com/aws/chalice)

## TODO
* Remove db and staticfiles after lambda destroy
