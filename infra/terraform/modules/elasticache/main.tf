variable "name" { type = string }
variable "environment" { type = string }
variable "tags" { type = map(string) }

# Redis cluster — session memory + semantic cache + Celery broker.
resource "aws_elasticache_replication_group" "this" {
  replication_group_id = "${var.name}-redis"
  description          = "FactoryMind Redis (${var.environment})"
  engine               = "redis"
  engine_version       = "7.1"
  node_type            = var.environment == "prod" ? "cache.r6g.large" : "cache.t4g.micro"
  num_node_groups         = var.environment == "prod" ? 3 : 1
  replicas_per_node_group = var.environment == "prod" ? 2 : 1
  automatic_failover_enabled = var.environment == "prod"
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true
  tags = var.tags
}

output "primary_endpoint" {
  value = aws_elasticache_replication_group.this.primary_endpoint_address
}
