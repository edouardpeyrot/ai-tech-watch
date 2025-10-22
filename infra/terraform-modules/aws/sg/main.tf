resource "aws_security_group" "lambda" {
  name   = "lambda-sg"
  vpc_id = var.aws_vpc

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "HTTPS"
    cidr_blocks = [var.subnet_privatea_cidr]
  }
}