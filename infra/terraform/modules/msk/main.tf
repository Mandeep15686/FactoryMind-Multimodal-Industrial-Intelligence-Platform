variable "name" { type = string }
variable "environment" { type = string }
variable "tags" { type = map(string) }

variable "subnet_ids" {
  type    = list(string)
  default = []
}

# Managed Streaming for Kafka — topics per plant/machine-type.
resource "aws_msk_cluster" "this" {
  cluster_name           = "${var.name}-kafka"
  kafka_version          = "3.6.0"
  number_of_broker_nodes = 3

  broker_node_group_info {
    instance_type   = var.environment == "prod" ? "kafka.m5.large" : "kafka.t3.small"
    client_subnets  = var.subnet_ids
    storage_info {
      ebs_storage_info {
        volume_size = 100
      }
    }
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
    }
  }
  tags = var.tags
}

output "bootstrap_brokers" {
  value = aws_msk_cluster.this.bootstrap_brokers_tls
}
