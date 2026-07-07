variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name — used as prefix for all resources"
  type        = string
  default     = "uptime-monitor"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16" # 65,536 IPs — more than enough
}

variable "db_username" {
  description = "RDS master username"
  type        = string
  default     = "uptime"
}

variable "db_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true # won't show in terraform plan/apply output
}

variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "uptime_monitor"
}

variable "eks_node_instance_type" {
  description = "EC2 instance type for EKS worker nodes"
  type        = string
  # default     = "t3.medium" # 2 vCPU, 4GB RAM — good balance of cost and performance
  default = "t3.small" # 2 vCPU, 2GB RAM — more cost-effective for small workloads

}

variable "eks_desired_nodes" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}
