output "lambda_name" {
  value = aws_lambda_function.this.function_name
}

output "schedule_name" {
  value = aws_scheduler_schedule.nightly.name
}
