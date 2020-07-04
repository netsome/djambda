terraform {
  backend "remote" {
    organization = "netsome"

    workspaces {
      name = "djambda"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "github" {}
