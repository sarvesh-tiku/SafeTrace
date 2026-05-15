variable "environment" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "oidc_provider" {
  type = string
}

variable "traces_bucket" {
  type = string
}

variable "results_bucket" {
  type = string
}

variable "jobs_queue_arn" {
  type = string
}
