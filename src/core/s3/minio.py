from dataclasses import dataclass
from typing import Any
from uuid import UUID

from aiobotocore.session import get_session  # type: ignore[import-untyped]
from botocore.config import Config  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]

from src.config import cfg

ALLOWED_MIME = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def is_allowed(content_type: str | None) -> bool:
    if not content_type:
        return False
    ct = content_type.split(";", 1)[0].lower()
    if ct.startswith("image/"):
        return True
    return ct in ALLOWED_MIME


@dataclass(frozen=True)
class PresignedPost:
    url: str
    fields: dict[str, str]
    key: str


class MinioPublic:
    def __init__(self, bucket: str) -> None:
        self.bucket = bucket

    async def _client(self) -> Any:
        session = get_session()
        return session.create_client(
            "s3",
            endpoint_url=cfg.minio.minio_endpoint,
            aws_access_key_id=cfg.minio.minio_access_key,
            aws_secret_access_key=cfg.minio.minio_secret_key,
            config=Config(
                region_name="us-east-1",
                s3={"addressing_style": "path"},
                max_pool_connections=50,
                connect_timeout=30,
                read_timeout=60,
            ),
        )

    def key_from_uuid(self, file_id: UUID) -> str:
        return str(file_id)

    def view_url(self, key: str) -> str:
        base = cfg.minio.minio_endpoint.rstrip("/")
        return f"{base}/{self.bucket}/{key}"

    async def presign_upload(
        self,
        *,
        file_id: UUID,
        content_type: str | None,
        size_bytes: int,
        expires_seconds: int | None = None,
        max_size_bytes: int | None = None,
    ) -> PresignedPost:
        exp = int(
            expires_seconds if expires_seconds is not None else cfg.minio.upload_expire_seconds
        )
        limit = int(
            max_size_bytes
            if max_size_bytes is not None
            else getattr(cfg.minio, "max_file_size_bytes", 50 * 1024 * 1024)
        )

        if size_bytes > limit:
            raise ValueError("FILE_TOO_LARGE")

        if not is_allowed(content_type):
            raise ValueError("FILE_TYPE_NOT_ALLOWED")

        key = self.key_from_uuid(file_id)

        fields: dict[str, str] = {"key": key}
        conditions: list[Any] = [
            {"key": key},
            ["content-length-range", 1, limit],
        ]

        ct = (content_type or "").split(";", 1)[0].strip()
        if ct:
            fields["Content-Type"] = ct
            conditions.append({"Content-Type": ct})

        async with await self._client() as s3:
            data = await s3.generate_presigned_post(
                Bucket=self.bucket,
                Key=key,
                Fields=fields,
                Conditions=conditions,
                ExpiresIn=exp,
            )

        return PresignedPost(url=data["url"], fields=data["fields"], key=key)

    async def finalize(self, *, key: str, max_size_bytes: int | None = None) -> dict[str, Any]:
        limit = int(
            max_size_bytes
            if max_size_bytes is not None
            else getattr(cfg.minio, "max_file_size_bytes", 50 * 1024 * 1024)
        )

        async with await self._client() as s3:
            head = await s3.head_object(Bucket=self.bucket, Key=key)

        size = int(head.get("ContentLength", 0))
        content_type = (head.get("ContentType") or "").split(";", 1)[0].lower()
        etag = (head.get("ETag") or "").strip('"')

        if size <= 0 or size > limit:
            raise ValueError("INVALID_FILE_SIZE")

        if not is_allowed(content_type):
            raise ValueError("INVALID_FILE_TYPE")

        return {
            "key": key,
            "size_bytes": size,
            "content_type": content_type,
            "etag": etag,
            "view_url": self.view_url(key),
        }

    # Юра, мне это нужно по модулю проект, пока не могу писать в тг на момент пуша этого файла.
    async def head_object(self, *, key: str) -> dict[str, Any]:
        async with await self._client() as s3:
            try:
                head = await s3.head_object(Bucket=self.bucket, Key=key)
            except ClientError as exc:
                raise ValueError("OBJECT_NOT_FOUND") from exc

        size = int(head.get("ContentLength", 0))
        content_type = (head.get("ContentType") or "").split(";", 1)[0].lower()
        etag = (head.get("ETag") or "").strip('"')

        return {
            "key": key,
            "size_bytes": size,
            "content_type": content_type,
            "etag": etag,
            "view_url": self.view_url(key),
        }

    async def remove_object(self, *, key: str) -> None:
        async with await self._client() as s3:
            await s3.delete_object(Bucket=self.bucket, Key=key)


minio_public = MinioPublic(bucket=cfg.minio.minio_bucket or "public")
minio_private = MinioPublic(bucket="private")
