variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "OpenSearch domain name"
  type        = string
  default     = "ai-devops-copilot"
}

variable "engine_version" {
  description = "OpenSearch engine version"
  type        = string
  default     = "OpenSearch_2.11"
}

variable "instance_type" {
  description = "Instance type for OpenSearch nodes"
  type        = string
  default     = "t3.small.search"
}

variable "instance_count" {
  description = "Number of instances in the cluster"
  type        = number
  default     = 2
}

variable "dedicated_master_enabled" {
  description = "Whether dedicated master nodes are enabled"
  type        = bool
  default     = false
}

variable "dedicated_master_type" {
  description = "Instance type for dedicated master nodes"
  type        = string
  default     = "t3.small.search"
}

variable "dedicated_master_count" {
  description = "Number of dedicated master nodes"
  type        = number
  default     = 3
}

variable "zone_awareness_enabled" {
  description = "Whether zone awareness is enabled"
  type        = bool
  default     = true
}

variable "availability_zone_count" {
  description = "Number of availability zones"
  type        = number
  default     = 2
}

variable "ebs_volume_size" {
  description = "Size of EBS volumes attached to data nodes (in GB)"
  type        = number
  default     = 20
}

variable "ebs_volume_type" {
  description = "Type of EBS volumes attached to data nodes"
  type        = string
  default     = "gp3"
}

variable "vpc_id" {
  description = "VPC ID where OpenSearch will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for OpenSearch"
  type        = list(string)
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access OpenSearch"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "master_user_name" {
  description = "Master username for OpenSearch"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "master_user_password" {
  description = "Master password for OpenSearch"
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Project   = "AI-DevOps-Copilot"
    ManagedBy = "Terraform"
  }
}
