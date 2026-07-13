variable "name" { type = string }
variable "environment" { type = string }
variable "tags" { type = map(string) }

# EKS cluster with a CPU node group + a GPU node group for HF inference pods.
resource "aws_eks_cluster" "this" {
  name     = var.name
  role_arn = aws_iam_role.cluster.arn
  version  = "1.30"

  vpc_config {
    subnet_ids = var.subnet_ids
  }
  tags = var.tags
}

variable "subnet_ids" {
  type    = list(string)
  default = []
}

resource "aws_iam_role" "cluster" {
  name = "${var.name}-eks-cluster"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "eks.amazonaws.com" }
    }]
  })
  tags = var.tags
}

resource "aws_eks_node_group" "cpu" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "${var.name}-cpu"
  node_role_arn   = aws_iam_role.cluster.arn
  subnet_ids      = var.subnet_ids
  instance_types  = ["m6i.xlarge"]
  scaling_config {
    desired_size = 4
    max_size     = 40
    min_size     = 2
  }
  tags = var.tags
}

resource "aws_eks_node_group" "gpu" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "${var.name}-gpu"
  node_role_arn   = aws_iam_role.cluster.arn
  subnet_ids      = var.subnet_ids
  instance_types  = ["g5.xlarge"]
  scaling_config {
    desired_size = 0
    max_size     = 8
    min_size     = 0
  }
  labels = { workload = "gpu-inference" }
  tags   = var.tags
}

output "cluster_name" {
  value = aws_eks_cluster.this.name
}
