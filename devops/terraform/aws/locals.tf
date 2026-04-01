# ==========================================
# Local Values
# ==========================================

locals {
  cluster_name = "${var.project_name}-${var.environment}-eks"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
  
  # Environment-specific configurations
  environment_config = {
    dev = {
      instance_types = ["t3.medium", "t3.large"]
      desired_size   = 1
      min_size       = 1
      max_size       = 3
      db_instance    = "db.t3.micro"
      redis_nodes    = 1
    }
    staging = {
      instance_types = ["m6i.xlarge"]
      desired_size   = 2
      min_size       = 1
      max_size       = 4
      db_instance    = "db.t3.medium"
      redis_nodes    = 2
    }
    production = {
      instance_types = ["m6i.2xlarge", "m6i.xlarge"]
      desired_size   = 3
      min_size       = 2
      max_size       = 10
      db_instance    = "db.r6g.xlarge"
      redis_nodes    = 2
    }
  }
}
