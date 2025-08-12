"""
S3 Manager Service for Quick Vendor
Handles all AWS S3 operations for product image storage
"""

import os
import uuid
import logging
from typing import Optional, BinaryIO, Dict, Any
from datetime import datetime
import mimetypes

from fastapi import HTTPException, status

# Configure logging
logger = logging.getLogger(__name__)

# Import boto3 only when needed
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
    BOTO3_AVAILABLE = True
except ImportError:
    logger.warning("boto3 not available - S3 functionality will be disabled")
    boto3 = None
    ClientError = Exception
    NoCredentialsError = Exception
    BotoCoreError = Exception
    BOTO3_AVAILABLE = False


class S3Manager:
    """
    S3 Manager class to handle all S3 operations for product images.
    
    This class encapsulates all S3 interactions including:
    - Uploading product images
    - Deleting product images
    - Generating unique filenames
    - Constructing S3 URLs
    """
    
    def __init__(self):
        """
        Initialize S3 client using environment variables.
        
        Environment variables required:
        - AWS_ACCESS_KEY_ID: AWS access key
        - AWS_SECRET_ACCESS_KEY: AWS secret key
        - AWS_REGION: AWS region (e.g., 'us-east-1')
        - S3_BUCKET_NAME: Name of the S3 bucket
        """
        # Import settings here to avoid circular imports
        from app.core.config import settings
        
        self.aws_access_key_id = settings.AWS_ACCESS_KEY_ID or os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = settings.AWS_REGION or os.getenv('AWS_REGION', 'us-east-1')
        self.bucket_name = settings.S3_BUCKET_NAME or os.getenv('S3_BUCKET_NAME')
        self.s3_client = None
        self.is_configured = False
        
        # Check if boto3 is available
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 not available - S3 functionality will be disabled")
            self.is_configured = False
            return
        
        # Check if S3 is configured
        if all([self.aws_access_key_id, self.aws_secret_access_key, self.bucket_name]):
            try:
                # Initialize S3 client
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.aws_region
                )
                self.is_configured = True
                logger.info(f"S3 client initialized successfully for bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {str(e)}")
                self.is_configured = False
        else:
            logger.warning("S3 not configured - missing required AWS environment variables. S3 functionality will be disabled.")
            self.is_configured = False
    
    def is_s3_configured(self) -> bool:
        """
        Check if S3 is properly configured and available.
        
        Returns:
            True if S3 is configured and available
        """
        return BOTO3_AVAILABLE and self.is_configured and self.s3_client is not None
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate a unique filename using UUID to prevent naming conflicts.
        
        Args:
            original_filename: The original filename from the upload
            
        Returns:
            A unique filename with UUID prefix
        """
        # Extract file extension
        file_extension = os.path.splitext(original_filename)[1].lower()
        
        # Generate unique filename with timestamp and UUID
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
        
        # Construct unique filename
        unique_filename = f"{timestamp}_{unique_id}{file_extension}"
        
        return unique_filename
    
    def _validate_image_file(self, filename: str, content_type: Optional[str] = None) -> None:
        """
        Validate that the uploaded file is an acceptable image format.
        
        Args:
            filename: The filename to validate
            content_type: The MIME type of the file
            
        Raises:
            HTTPException: If file format is not acceptable
        """
        # Allowed image extensions
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        
        # Allowed MIME types
        allowed_mime_types = {
            'image/jpeg', 'image/jpg', 'image/png', 
            'image/gif', 'image/webp', 'image/bmp'
        }
        
        # Check file extension
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        # Check MIME type if provided
        if content_type and content_type not in allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type. Allowed types: {', '.join(allowed_mime_types)}"
            )
    
    async def upload_product_image(
        self, 
        file_content: BinaryIO, 
        filename: str,
        product_id: int,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a product image to S3 bucket.
        
        Args:
            file_content: Binary file content to upload
            filename: Original filename
            product_id: ID of the product this image belongs to
            content_type: MIME type of the file
            
        Returns:
            Dictionary containing:
                - url: Public URL of the uploaded image
                - key: S3 object key
                - filename: The unique filename generated
                
        Raises:
            HTTPException: On upload failure or if S3 is not configured
        """
        if not self.is_s3_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="S3 storage is not configured. Please contact support."
            )
        
        try:
            # Validate image file
            self._validate_image_file(filename, content_type)
            
            # Generate unique filename
            unique_filename = self._generate_unique_filename(filename)
            
            # Construct S3 object key with folder structure
            s3_key = f"qv-products-img/{product_id}/{unique_filename}"
            
            # Determine content type if not provided
            if not content_type:
                content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            # Upload file to S3
            logger.info(f"Uploading image to S3: {s3_key}")
            
            # Note: ACL is not set here because the bucket has ACLs disabled
            # Public access is managed through bucket policy instead
            self.s3_client.upload_fileobj(
                file_content,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ContentDisposition': 'inline',  # Display in browser instead of download
                    'CacheControl': 'max-age=31536000',  # Cache for 1 year
                    'Metadata': {
                        'product_id': str(product_id),
                        'original_filename': filename,
                        'upload_timestamp': datetime.utcnow().isoformat()
                    }
                }
            )
            
            # Construct public URL
            # Format: https://{bucket_name}.s3.{region}.amazonaws.com/{key}
            public_url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Successfully uploaded image: {public_url}")
            
            return {
                "url": public_url,
                "key": s3_key,
                "filename": unique_filename,
                "product_id": product_id,
                "upload_timestamp": datetime.utcnow().isoformat()
            }
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AWS credentials configuration error. Please contact support."
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"AWS S3 ClientError: {error_code} - {error_message}")
            
            if error_code == 'AccessDenied':
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to S3 bucket. Please check IAM permissions."
                )
            elif error_code == 'NoSuchBucket':
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="S3 bucket not found. Please check configuration."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload image: {error_message}"
                )
                
        except BotoCoreError as e:
            logger.error(f"BotoCore error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to connect to AWS S3. Please try again later."
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during image upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during image upload."
            )
    
    async def delete_product_image(self, s3_key: str) -> bool:
        """
        Delete a product image from S3 bucket.
        
        Args:
            s3_key: The S3 object key to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: On deletion failure or if S3 is not configured
        """
        if not self.is_s3_configured():
            logger.warning(f"Attempted to delete S3 image {s3_key} but S3 is not configured")
            return True  # Return True to avoid blocking product deletion
        
        try:
            logger.info(f"Deleting image from S3: {s3_key}")
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"Successfully deleted image: {s3_key}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"Failed to delete image: {error_code} - {error_message}")
            
            if error_code == 'AccessDenied':
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to delete S3 object."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete image: {error_message}"
                )
                
        except Exception as e:
            logger.error(f"Unexpected error during image deletion: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during image deletion."
            )
    
    async def delete_all_product_images(self, product_id: int) -> int:
        """
        Delete all images for a specific product.
        
        Args:
            product_id: ID of the product whose images should be deleted
            
        Returns:
            Number of images deleted
        """
        if not self.is_s3_configured():
            logger.warning(f"Attempted to delete S3 images for product {product_id} but S3 is not configured")
            return 0
        
        try:
            prefix = f"qv-products-img/{product_id}/"
            
            # List all objects with the prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                logger.info(f"No images found for product {product_id}")
                return 0
            
            # Delete all objects
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
            
            if objects_to_delete:
                self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects_to_delete}
                )
                
                deleted_count = len(objects_to_delete)
                logger.info(f"Deleted {deleted_count} images for product {product_id}")
                return deleted_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Error deleting images for product {product_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete product images."
            )
    
    def get_image_url_from_key(self, s3_key: str) -> str:
        """
        Generate the public URL for an S3 object key.
        
        Args:
            s3_key: The S3 object key
            
        Returns:
            The public URL for the object
        """
        return f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
    
    async def validate_s3_connection(self) -> bool:
        """
        Validate that the S3 connection and permissions are working.
        
        Returns:
            True if connection is valid and bucket is accessible
        """
        if not self.is_s3_configured():
            return False
        
        try:
            # Try to get bucket location (minimal permission required)
            self.s3_client.get_bucket_location(Bucket=self.bucket_name)
            logger.info("S3 connection validated successfully")
            return True
            
        except ClientError as e:
            logger.error(f"S3 connection validation failed: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during S3 validation: {str(e)}")
            return False


# Create a singleton instance
s3_manager = None

def get_s3_manager() -> S3Manager:
    """
    Get or create the S3Manager singleton instance.
    
    Returns:
        S3Manager instance
    """
    global s3_manager
    if s3_manager is None:
        s3_manager = S3Manager()  # Will not raise exception now
    return s3_manager
