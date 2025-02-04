resource "aws_iam_user" "bedrock_user" {
  name = "eepbot-bedrock-user"
}

resource "aws_iam_access_key" "bedrock_user_key" {
  user = aws_iam_user.bedrock_user.name
}

resource "aws_ssm_parameter" "bedrock_user_access_key_id" {
  name        = var.ssm_access_key_path
  description = "Access Key ID for example-terraform-user"
  type        = "String"
  value       = aws_iam_access_key.bedrock_user_key.id
}

resource "aws_ssm_parameter" "bedrock_user_secret_access_key" {
  name        = var.ssm_secret_key_path
  description = "Secret Access Key for example-terraform-user"
  type        = "SecureString"
  value       = aws_iam_access_key.bedrock_user_key.secret
}

resource "aws_iam_policy" "bedrock_policy" {
  name        = "BedrockFullAccessPolicy"
  description = "Allows full access to AWS Bedrock models"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "bedrock:InvokeModel",
          "bedrock:Converse",
          "bedrock:ListFoundationModels"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "attach_bedrock_policy" {
  user       = aws_iam_user.bedrock_user.name
  policy_arn = aws_iam_policy.bedrock_policy.arn
}
