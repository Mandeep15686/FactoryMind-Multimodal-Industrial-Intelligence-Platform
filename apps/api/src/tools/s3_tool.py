"""AWS S3 tool — store defect images/audio/reports, mint presigned URLs."""
from __future__ import annotations

import logging

from src.core.config import settings
from src.tools._base import tool

logger = logging.getLogger("factorymind.tools.s3")


def _client():  # pragma: no cover
    import boto3

    return boto3.client("s3", region_name=settings.aws_region)


def put_object(key: str, data: bytes) -> str:
    """Upload bytes to S3; returns the s3:// URL."""
    try:  # pragma: no cover
        _client().put_object(Bucket=settings.s3_bucket, Key=key, Body=data)
    except Exception as exc:
        logger.info("MOCK S3 put s3://%s/%s (%s)", settings.s3_bucket, key, exc)
    return f"s3://{settings.s3_bucket}/{key}"


def presign(key: str, expires: int = 3600) -> str:
    """Return a presigned GET URL for a stored object."""
    try:  # pragma: no cover
        return _client().generate_presigned_url(
            "get_object", Params={"Bucket": settings.s3_bucket, "Key": key}, ExpiresIn=expires
        )
    except Exception:
        return f"https://{settings.s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{key}?X-Mock=1"


s3_put_object = tool(put_object)
s3_presign = tool(presign)
