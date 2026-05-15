output "agent_service_role_arn" {
  value = aws_iam_role.agent_service.arn
}

output "tracer_service_role_arn" {
  value = aws_iam_role.tracer_service.arn
}

output "results_service_role_arn" {
  value = aws_iam_role.results_service.arn
}
