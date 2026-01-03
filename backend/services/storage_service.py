import os
import hashlib
from typing import Optional
from pathlib import Path
from fastapi import UploadFile
from config import settings

class StorageService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_upload(self, file: UploadFile, prefix: str = "report") -> str:
        if not self._is_allowed_extension(file.filename):
            raise ValueError(f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}")
        
        file_content = await file.read()
        
        if len(file_content) > settings.MAX_UPLOAD_SIZE:
            raise ValueError(f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes")
        
        file_hash = hashlib.sha256(file_content).hexdigest()[:16]
        extension = Path(file.filename).suffix
        filename = f"{prefix}_{file_hash}{extension}"
        
        file_path = self.upload_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return str(file_path)
    
    def _is_allowed_extension(self, filename: str) -> bool:
        extension = Path(filename).suffix.lower()
        return extension in settings.ALLOWED_EXTENSIONS
    
    def get_file_path(self, filename: str) -> Optional[Path]:
        file_path = self.upload_dir / filename
        if file_path.exists():
            return file_path
        return None
    
    def delete_file(self, filename: str) -> bool:
        file_path = self.upload_dir / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False

storage_service = StorageService()
