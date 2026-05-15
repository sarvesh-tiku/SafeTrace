resource "aws_sqs_queue" "dlq" {
  name                      = "safetrace-jobs-dlq-${var.environment}"
  message_retention_seconds = 1209600  # 14 days
  tags                      = { Environment = var.environment }
}

resource "aws_sqs_queue" "jobs" {
  name                       = "safetrace-jobs-${var.environment}"
  visibility_timeout_seconds = 30
  message_retention_seconds  = 86400
  max_message_size           = 262144

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })

  tags = { Environment = var.environment }
}
