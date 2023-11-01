terraform {
  backend "remote" {
    organization = "ensembletf"

    workspaces {
      name = "djambda"
    }
  }
  required_version = "1.6.2"
}

provider "aws" {
  region = var.aws_region
}

provider "github" {}
