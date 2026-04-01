# ==========================================
# Terraform Variables
# ==========================================

variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "ap-southeast-1"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "robot-diagnosis"
}

# ==========================================
# VPC Variables
# ==========================================
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnets" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# ==========================================
# EKS Variables
# ==========================================
variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS nodes"
  type        = list(string)
  default     = ["m6i.xlarge", "m6i.2xlarge"]
}

variable "node_desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 5
}

variable "monitoring_node_desired_size" {
  description = "Desired number of monitoring nodes"
  type        = number
  default     = 1
}

variable "monitoring_node_min_size" {
  description = "Minimum number of monitoring nodes"
  type        = number
  default     = 1
}

variable "monitoring_node_max_size" {
  description = "Maximum number of monitoring nodes"
  type        = number
  default     = 3
}

# ==========================================
# RDS Variables
# ==========================================
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "RDS maximum allocated storage in GB"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "robot_diagnosis"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "admin"
}

# ==========================================
# ElastiCache Variables
# ==========================================
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 1
}

# ==========================================
# Networking Variables
# ==========================================
variable "allowed_cidr_blocks" {
  description = "Allowed CIDR blocks for security groups"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "robot-diagnosis.example.com"
}

variable "create_route53_zone" {
  description = "Whether to create Route53 zone"
  type        = bool
  default     = false
}

variable "route53_zone_id" {
  description = "Route53 zone ID (if not creating new zone)"
  type        = string
  default     = ""
}
