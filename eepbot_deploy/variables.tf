variable "deployment_type" {
  type = string 
  default = "local" # local, remote
}

variable "discord_bot_token" {
  type = string
}

variable "mistral_api_token" {
  type = string 
}

variable "openrouter_api_token" {
  type = string 
}

variable "history_length" {
  type = number
  default = 40
}

