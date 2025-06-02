# core/validators.py
import os
import magic
import mimetypes
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.conf import settings


class ImageValidator:
    """
    Comprehensive image validator that checks:
    1. File extensions
    2. MIME types
    3. Magic numbers (file signatures)
    4. File size
    """

    # Allowed image extensions
    ALLOWED_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif'
    }

    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/bmp',
        'image/tiff',
        'image/x-ms-bmp'
    }

    # Magic numbers (file signatures) for common image formats
    MAGIC_NUMBERS = {
        # JPEG
        b'\xff\xd8\xff': 'image/jpeg',
        # PNG
        b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a': 'image/png',
        # GIF87a
        b'\x47\x49\x46\x38\x37\x61': 'image/gif',
        # GIF89a
        b'\x47\x49\x46\x38\x39\x61': 'image/gif',
        # WebP
        b'\x52\x49\x46\x46': 'image/webp',  # RIFF header (need to check WEBP signature later)
        # BMP
        b'\x42\x4d': 'image/bmp',
        # TIFF (little endian)
        b'\x49\x49\x2a\x00': 'image/tiff',
        # TIFF (big endian)
        b'\x4d\x4d\x00\x2a': 'image/tiff',
    }

    def __init__(self, max_size_mb=10):
        """
        Initialize validator with maximum file size in MB
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024

    def __call__(self, file):
        """
        Main validation method
        """
        if not file:
            return

        # Get file extension
        file_extension = self._get_file_extension(file.name)

        # Validate extension
        if file_extension.lower() not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f'File extension "{file_extension}" is not allowed. '
                f'Allowed extensions: {", ".join(sorted(self.ALLOWED_EXTENSIONS))}'
            )

        # Validate file size
        if file.size > self.max_size_bytes:
            raise ValidationError(
                f'File size ({file.size / (1024 * 1024):.1f}MB) exceeds maximum allowed size '
                f'({self.max_size_bytes / (1024 * 1024):.0f}MB)'
            )

        # Read file content for magic number validation
        file_content = self._read_file_content(file)

        # Validate magic numbers
        detected_mime = self._validate_magic_numbers(file_content)

        # Validate MIME type using Django's file detection
        mime_type, _ = mimetypes.guess_type(file.name)
        if mime_type and mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValidationError(
                f'MIME type "{mime_type}" is not allowed. '
                f'Only image files are permitted.'
            )

        # Additional validation using python-magic if available
        try:
            magic_mime = magic.from_buffer(file_content, mime=True)
            if magic_mime not in self.ALLOWED_MIME_TYPES:
                raise ValidationError(
                    f'File appears to be "{magic_mime}" which is not an allowed image format.'
                )
        except Exception:
            # python-magic not available or failed, rely on other checks
            pass

        # Validate that detected magic number matches expected type
        if detected_mime and mime_type:
            if not self._mime_types_compatible(detected_mime, mime_type):
                raise ValidationError(
                    'File content does not match file extension. '
                    'This might be a disguised malicious file.'
                )

    def _get_file_extension(self, filename):
        """Get file extension from filename"""
        return os.path.splitext(filename)[1].lower()

    def _read_file_content(self, file):
        """Safely read file content for validation"""
        try:
            # Save current position
            current_position = file.tell()

            # Read from beginning
            file.seek(0)
            content = file.read(8192)  # Read first 8KB for magic number detection

            # Restore position
            file.seek(current_position)

            return content
        except Exception as e:
            raise ValidationError(f'Unable to read file content: {str(e)}')

    def _validate_magic_numbers(self, content):
        """Validate file magic numbers/signatures"""
        if not content:
            raise ValidationError('File appears to be empty')

        # Check magic numbers
        for magic_bytes, mime_type in self.MAGIC_NUMBERS.items():
            if content.startswith(magic_bytes):
                # Special handling for WebP (need to check WEBP signature)
                if magic_bytes == b'\x52\x49\x46\x46' and len(content) >= 12:
                    if content[8:12] == b'WEBP':
                        return 'image/webp'
                    else:
                        continue  # It's RIFF but not WebP
                return mime_type

        # If no magic number matches, it might still be a valid image
        # but we should be suspicious
        raise ValidationError(
            'File does not appear to be a valid image file. '
            'The file signature is not recognized.'
        )

    def _mime_types_compatible(self, detected_mime, declared_mime):
        """Check if detected MIME type is compatible with declared type"""
        # Handle variations in JPEG MIME types
        jpeg_types = {'image/jpeg', 'image/jpg', 'image/pjpeg'}
        tiff_types = {'image/tiff', 'image/tif'}

        if detected_mime in jpeg_types and declared_mime in jpeg_types:
            return True
        if detected_mime in tiff_types and declared_mime in tiff_types:
            return True

        return detected_mime == declared_mime


class MultipleImageValidator:
    """
    Validator for multiple image uploads with count limits
    """

    def __init__(self, max_count=5, max_size_mb=10):
        self.max_count = max_count
        self.image_validator = ImageValidator(max_size_mb=max_size_mb)

    def __call__(self, files):
        """
        Validate multiple files
        """
        if not files:
            return

        # Handle single file case
        if not isinstance(files, (list, tuple)):
            files = [files]

        # Check count limit
        if len(files) > self.max_count:
            raise ValidationError(
                f'Too many files uploaded. Maximum allowed: {self.max_count}, '
                f'received: {len(files)}'
            )

        # Validate each file
        for i, file in enumerate(files):
            try:
                self.image_validator(file)
            except ValidationError as e:
                raise ValidationError(f'File {i + 1}: {str(e)}')


# Convenience validator instances
validate_image = ImageValidator(max_size_mb=10)
validate_multiple_images = MultipleImageValidator(max_count=5, max_size_mb=10)