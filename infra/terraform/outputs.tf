output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "traces_bucket" {
  description = "S3 bucket for traces"
  value       = module.s3.traces_bucket_name
}

output "results_bucket" {
  description = "S3 bucket for results"
  value       = module.s3.results_bucket_name
}

output "jobs_queue_url" {
  description = "SQS jobs queue URL"
  value       = module.sqs.jobs_queue_url
}
