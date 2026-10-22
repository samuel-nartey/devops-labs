terraform {
  required_providers {
    random = {
      source = "hashicorp/random"
    }
  }
}

resource "random_pet" "demo" {
  length = 3
}

output "pet_name" {
  value = random_pet.demo.id
}
