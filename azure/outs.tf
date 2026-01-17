output "storage_account_url" {
  description = "Azure Storage Account Blob service URL"
  value       = azurerm_storage_account.bucket_sa.primary_blob_endpoint
}

output "blob_container_name" {
  description = "Azure Blob Storage container name"
  value       = azurerm_storage_container.bucket.name
}