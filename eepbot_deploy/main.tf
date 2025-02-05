resource "docker_image" "eepbot" {
  name = "eepbot_py"
  build {
    context = ".."
    dockerfile = "../eepbot.Dockerfile"
    tag     = ["eepbot:local"]
    label = {
      author : "sleep"
    }
  }
}

# module "bedrock" {
#   source = "./bedrock"
# }

# data "aws_ssm_parameter" "app_access_key_id" {
#   name = module.bedrock.ssm_access_key_path 
#   depends_on = [module.bedrock]
# }

# data "aws_ssm_parameter" "app_secret_access_key" {
#   name = module.bedrock.ssm_secret_key_path
#   with_decryption = true
#   depends_on = [module.bedrock]
# }

resource "docker_image" "seq" {
    name = "datalust/seq:latest"
}

resource "docker_network" "network" {
  name = "eepbot-network"
}

resource "docker_container" "seq" {
  name = "seq"
  image = docker_image.seq.image_id
  ports {
    internal = 5341
    external = 5341
  }
  ports {
    internal = 80
    external = 5342
  }
  networks_advanced {
    name = docker_network.network.name
  }
  volumes {
    container_path = "/data"
    host_path = "/home/sleep/projects/eepbot/deployment/seq" #TODO
  }
  env = [
    "ACCEPT_EULA=Y"
  ]
}

resource "docker_container" "eepbot" {
  name = "eepbot-${var.deployment_type}"
  image = docker_image.eepbot.image_id
  networks_advanced {
    name = docker_network.network.name
  }
  env = [ 
    "SLEEPY_HISTORY_LENGTH=${var.history_length}",
    "DISCORD_BOT_TOKEN=${var.discord_bot_token}",
    "MISTRAL_API_TOKEN=${var.mistral_api_token}",
    "OPENROUTER_API_TOKEN=${var.openrouter_api_token}",
    # "AWS_REGION=${var.aws_region}",
    # "AWS_ACCESS_KEY_ID=${data.aws_ssm_parameter.app_access_key_id.value}",
    # "AWS_SECRET_ACCESS_KEY=${data.aws_ssm_parameter.app_secret_access_key.value}"
  ]
}