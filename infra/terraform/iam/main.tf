data "aws_caller_identity" "current" {}

locals {
  account_id   = data.aws_caller_identity.current.account_id
  oidc_sub     = replace(var.oidc_provider, "https://", "")
}

# Agent service role - SQS read + S3 write
resource "aws_iam_role" "agent_service" {
  name = "safetrace-agent-service-${var.environment}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Federated = var.oidc_provider }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "${local.oidc_sub}:sub" = "system:serviceaccount:safetrace:agent-service"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "agent_service" {
  name = "agent-service-policy"
  role = aws_iam_role.agent_service.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
        Resource = var.jobs_queue_arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:PutObject", "s3:GetObject"]
        Resource = "arn:aws:s3:::${var.traces_bucket}/*"
      }
    ]
  })
}

# Tracer service role - S3 write
resource "aws_iam_role" "tracer_service" {
  name = "safetrace-tracer-service-${var.environment}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Federated = var.oidc_provider }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "${local.oidc_sub}:sub" = "system:serviceaccount:safetrace:tracer-service"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "tracer_service" {
  name = "tracer-service-policy"
  role = aws_iam_role.tracer_service.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:PutObject"]
      Resource = "arn:aws:s3:::${var.traces_bucket}/*"
    }]
  })
}

# Results service role - S3 read/write
resource "aws_iam_role" "results_service" {
  name = "safetrace-results-service-${var.environment}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Federated = var.oidc_provider }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "${local.oidc_sub}:sub" = "system:serviceaccount:safetrace:results-service"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "results_service" {
  name = "results-service-policy"
  role = aws_iam_role.results_service.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
        Resource = [
          "arn:aws:s3:::${var.results_bucket}",
          "arn:aws:s3:::${var.results_bucket}/*"
        ]
      }
    ]
  })
}
