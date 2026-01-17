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
resource "azurerm_storage_account" "bucket_sa" {
     name                     = "st${local.application}${local.environment}${local.region_code}"
     resource_group_name      = azurerm_resource_group.rg.name
     location                 = azurerm_resource_group.rg.location

     account_tier             = "Standard"
     account_replication_type = "LRS"        
          
     # Locally  Redudant Storage - (LRS)  3 replicas within same AZes
     # Zone     Redudant Storage - (ZRS)  3 replicas across different AZes
     # Geo      Redudant Storage - (GRS)  3 replicas across different regions
     # Geo-Zone Redudant Storage - (GZRS) 3 replicas across different regions and AZes
}


resource "azurerm_storage_container" "bucket" {
     name                  = "blobstorage"
     storage_account_name  = azurerm_storage_account.bucket_sa.name
     container_access_type = "private"
}
