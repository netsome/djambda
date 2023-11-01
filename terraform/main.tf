terraform {
  backend "remote" {
    organization = "ensembletf"

    workspaces {
      name = "djambda"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "github" {}
