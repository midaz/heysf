"""
S3 storage service for document storage.
"""
import logging
from typing import Optional
from io import BytesIO
import boto3
from botocore.exceptions import ClientError

from ..config import settings

logger = logging.getLogger(__name__)


class S3StorageService:
    """Service for handling document storage in S3."""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket_name = settings.aws_s3_bucket
    
    def upload_text_content(self, content: str, file_key: str) -> bool:
        """
        Upload text content to S3.
        
        Args:
            content: Text content to upload
            file_key: S3 key for the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert string to bytes
            content_bytes = content.encode('utf-8')
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=content_bytes,
                ContentType='text/plain'
            )
            
            logger.info(f"Successfully uploaded content to S3: {file_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading to S3: {e}")
            return False
    
    def download_text_content(self, file_key: str) -> Optional[str]:
        """
        Download text content from S3.
        
        Args:
            file_key: S3 key for the file
            
        Returns:
            Text content if successful, None otherwise
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            content = response['Body'].read().decode('utf-8')
            logger.info(f"Successfully downloaded content from S3: {file_key}")
            return content
            
        except ClientError as e:
            logger.error(f"Error downloading from S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading from S3: {e}")
            return None
    
    def file_exists(self, file_key: str) -> bool:
        """
        Check if a file exists in S3.
        
        Args:
            file_key: S3 key for the file
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except ClientError:
            return False
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            file_key: S3 key for the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"Successfully deleted file from S3: {file_key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting from S3: {e}")
            return False 