variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "function_name" {
  type    = string
  default = "s3-lifecycle-enforcer"
}

variable "lambda_zip" {
  type        = string
  description = "Path to the packaged Lambda zip."
}

variable "dry_run" {
  type    = string
  default = "true"
}

variable "size_threshold_bytes" {
  type    = number
  default = 107374182400
}
