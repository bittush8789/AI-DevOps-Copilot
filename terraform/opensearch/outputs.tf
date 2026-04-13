output "domain_id" {
  description = "Unique identifier for the domain"
  value       = aws_opensearch_domain.main.domain_id
}

output "domain_name" {
  description = "Name of the OpenSearch domain"
  value       = aws_opensearch_domain.main.domain_name
}

output "endpoint" {
  description = "Domain-specific endpoint used to submit index, search, and data upload requests"
  value       = aws_opensearch_domain.main.endpoint
}

output "kibana_endpoint" {
  description = "Domain-specific endpoint for Kibana"
  value       = aws_opensearch_domain.main.kibana_endpoint
}

output "arn" {
  description = "ARN of the domain"
  value       = aws_opensearch_domain.main.arn
}

output "security_group_id" {
  description = "Security group ID for OpenSearch"
  value       = aws_security_group.opensearch.id
}
