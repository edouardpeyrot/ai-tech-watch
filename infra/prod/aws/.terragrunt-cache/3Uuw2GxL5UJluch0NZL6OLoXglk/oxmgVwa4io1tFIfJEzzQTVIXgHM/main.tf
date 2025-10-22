terraform {
  backend "s3" {}
}

module "vpc" {
  source = "../vpc"
  cidr_block = var.vpc_cidr
}

resource "aws_subnet" "private_a" {
  vpc_id            = var.aws_vpc
  cidr_block        = var.subnet_privatea_cidr
  availability_zone = var.aws_region
}
