
# Lambda function
resource "aws_lambda_function" "example" {
  filename         = "lambda.zip"
  function_name    = "python tech watch lambda function"
  role             = var.lambda_iam_role
  handler          = "index.handler"

  runtime = "python 3.12"

  environment {
    variables = {
      ENVIRONMENT = "production"
      LOG_LEVEL   = "info"
    }
  }

  tags = {
    Environment = "production"
    Application = "ai-tech-watch"
  }
}