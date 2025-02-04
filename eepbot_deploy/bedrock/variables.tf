variable "ssm_access_key_path" {
  type = string
  default = "/eepbot/aws_access_key_id"
}

variable "ssm_secret_key_path" {
  type = string
  default = "/eepbot/aws_secret_access_key"
}