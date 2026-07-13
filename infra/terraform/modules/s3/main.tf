variable "name" { type = string }
variable "environment" { type = string }
variable "tags" { type = map(string) }

# Artifact bucket — defect images, audio windows, generated reports.
resource "aws_s3_bucket" "artifacts" {
  bucket = "${var.name}-artifacts"
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  rule {
    id     = "expire-raw-frames"
    status = "Enabled"
    filter { prefix = "frames/" }
    expiration { days = 90 }
  }
}

output "bucket_name" {
  value = aws_s3_bucket.artifacts.id
}
