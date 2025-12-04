terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
    }
  }
}

provider "docker" {}


resource "docker_image" "nginx" {
  name = "nginx:latest"
}

resource "docker_volume" "nginx_data" {}

resource "docker_container" "nginx_server" {
  name  = "nginx-server"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = 8080
  }

  mounts {
    target = "/usr/share/nginx/html"
    source = docker_volume.nginx_data.name
    type   = "volume"
  }
}

resource "docker_image" "flask" {
  name = "flask-backend"

  build {
    context    = "${path.module}/backend"
    dockerfile = "Dockerfile"
  }
}

resource "docker_container" "flask_server" {
  name  = "flask-server"
  image = docker_image.flask.image_id

  ports {
    internal = 5000
    external = 5000
  }
}
