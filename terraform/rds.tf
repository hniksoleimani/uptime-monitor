# ===========================================================
# RDS Subnet Group
# ===========================================================
# Tells RDS which subnets it can use. We use private subnets
# so the database is never exposed to the internet.

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet"
  subnet_ids = aws_subnet.private[*].id

  tags = { Name = "${var.project_name}-db-subnet" }
}

# ===========================================================
# RDS PostgreSQL Instance
# ===========================================================

resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-db"

  # Engine
  engine         = "postgres"
  engine_version = "16.6"

  # Size — db.t3.micro is free-tier eligible
  instance_class    = "db.t3.micro"
  allocated_storage = 20 # GB
  storage_type      = "gp3"

  # Database
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  # Network
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false # IMPORTANT: no internet access

  # Backups & maintenance
  backup_retention_period = 1
  skip_final_snapshot     = true # set to false in real production

  # Encryption
  storage_encrypted = true

  tags = { Name = "${var.project_name}-db" }
}
