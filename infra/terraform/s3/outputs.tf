output "traces_bucket_name" {
  value = aws_s3_bucket.traces.bucket
}

output "results_bucket_name" {
  value = aws_s3_bucket.results.bucket
}

output "traces_bucket_arn" {
  value = aws_s3_bucket.traces.arn
}

output "results_bucket_arn" {
  value = aws_s3_bucket.results.arn
}
