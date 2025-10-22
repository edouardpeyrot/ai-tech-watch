locals {
  cloud = "aws"
  env = "prod"
  region = "eu-west-3"
  prefix = "${local.env}-${local.cloud}"
  bucket_name = "tfstate-${local.cloud}-${local.env}"
  dynamodb_table = "terraform-locks-${local.cloud}"
}

remote_state {
  backend = "s3"
  config = {
    bucket         = local.bucket_name
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = local.region
    encrypt        = true
    dynamodb_table = local.dynamodb_table
  }
}

terraform {
  extra_arguments "common_vars" {
    commands = ["plan", "apply", "destroy"]
    arguments = ["-var", "region=${local.region}"]
  }
}

inputs = {
  region     = local.region
  cidr_block = local.cloud
  env_name   = local.env
}
