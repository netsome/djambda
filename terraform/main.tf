terraform {
  backend "remote" {
    organization = "djambda"

    workspaces {
      name = "test"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "github" {}
