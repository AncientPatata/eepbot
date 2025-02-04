output "user_access_key_id" {
  description = "The access key ID for created user"
  value       = aws_iam_access_key.bedrock_user_key.id
}

output "ssm_access_key_path" {
    value = aws_ssm_parameter.bedrock_user_access_key_id.name
}

output "ssm_secret_key_path" {
    value = aws_ssm_parameter.bedrock_user_secret_access_key.name
}