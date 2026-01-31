import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from app.core.config import settings


class StorageService:
    """Handle S3 video storage"""
    
    @staticmethod
    def get_s3_client():
        """Get configured S3 client"""
        config = Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'}
        )
        
        return boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
            config=config
        )
    
    @staticmethod
    async def generate_upload_url(clip_id: str, file_size: int, expires_in: int = 300) -> str:
        """
        Generate presigned S3 upload URL
        Frontend uploads video directly to S3 using this URL
        """
        s3_client = StorageService.get_s3_client()
        
        key = f"clips/{clip_id}.mp4"
        
        try:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': settings.S3_BUCKET_NAME,
                    'Key': key,
                    'ContentType': 'video/mp4'
                },
                ExpiresIn=expires_in
            )
            return presigned_url
        except ClientError as e:
            raise Exception(f"Failed to generate upload URL: {str(e)}")
    
    @staticmethod
    async def get_clip_url(clip_id: str) -> str:
        """Get public/signed URL for viewing a clip"""
        # If bucket is public, return direct URL
        if settings.S3_ENDPOINT_URL:
            return f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/clips/{clip_id}.mp4"
        else:
            return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.S3_REGION}.amazonaws.com/clips/{clip_id}.mp4"
    
    @staticmethod
    async def delete_clip(clip_id: str) -> bool:
        """Delete a clip from S3"""
        s3_client = StorageService.get_s3_client()
        key = f"clips/{clip_id}.mp4"
        
        try:
            s3_client.delete_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=key
            )
            return True
        except ClientError:
            return False
