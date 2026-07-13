variable "name" { type = string }
variable "environment" { type = string }
variable "tags" { type = map(string) }

# PostgreSQL 16 Multi-AZ (TimescaleDB + pgvector installed via extensions).
resource "aws_db_instance" "this" {
  identifier            = "${var.name}-pg"
  engine                = "postgres"
  engine_version        = "16.3"
  instance_class        = var.environment == "prod" ? "db.r6g.xlarge" : "db.t4g.medium"
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_encrypted     = true
  multi_az              = var.environment == "prod"
  db_name               = "factorymind"
  username              = "factory"
  manage_master_user_password = true
  backup_retention_period     = 7
  skip_final_snapshot         = var.environment != "prod"
  tags                        = var.tags
}

output "endpoint" {
  value = aws_db_instance.this.endpoint
}
