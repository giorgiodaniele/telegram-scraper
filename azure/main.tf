terraform {
  required_version = ">= 0.14"
  required_providers {
     azurerm = {
          source  = "registry.terraform.io/hashicorp/azurerm"
          version = "~> 3.1.0"
     }
  }
}

provider "azurerm" {
  features {}
}

# Create a new resource group
resource "azurerm_resource_group" "rg" {
     name     = "rg-${local.application}-${local.environment}-${local.region_code}"
     location = "${local.region}"

     tags = {
     environment = "${local.environment}"
     application = "${local.application}"
     team        = "${local.team}"
     }

}


# Create a new storage account
resource "azurerm_storage_account" "storage" {
     name                     = "st${local.application}${local.environment}${local.region_code}"
     resource_group_name      = azurerm_resource_group.rg.name
     location                 = azurerm_resource_group.rg.location

     account_tier             = "Standard"
     account_replication_type = "LRS"        
          
     # LRS  - 3 synchronous replicas within a single datacenter
     # ZRS  - 3 synchronous replicas across different availability zones
     # GRS  - LRS in primary region + async replication to secondary region (6 total copies)
     # GZRS - ZRS in primary region + async replication to secondary region
}


resource "azurerm_storage_container" "main_container" {
     name                  = "data"
     storage_account_name  = azurerm_storage_account.storage.name
     container_access_type = "private"
}
