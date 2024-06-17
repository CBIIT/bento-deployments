terraform {
  required_providers {
    aws = {
        source  = "hashicorp/aws"
        #version = "4.17.1"
        #version = ">=4.66.1"
        version = ">=5.16.0"
    }
  }
}

provider "aws" {
  region = var.region
}