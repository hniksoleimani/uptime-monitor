terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0" # any 5.x version
    }
  }

  # Remote state storage — uncomment after creating the S3 bucket
  # This keeps your terraform state file in S3 instead of locally,
  # so your team (or CI/CD) can share the same state.
  #
  # backend "s3" {
  #   bucket = "uptime-monitor-tfstate"
  #   key    = "terraform.tfstate"
  #   region = "eu-central-1"
  #   dynamodb_table = "terraform-locks" 
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      ManagedBy   = "terraform"
      Environment = "production"
    }
  }
}
