from typing import Optional
from config import settings

class DigiLockerAdapter:
    def __init__(self):
        self.enabled = settings.DIGILOCKER_ENABLED
        self.client_id = settings.DIGILOCKER_CLIENT_ID
        self.client_secret = settings.DIGILOCKER_CLIENT_SECRET
    
    def get_authorization_url(self, redirect_uri: str) -> str:
        if not self.enabled:
            return self._mock_authorization_url(redirect_uri)
        
        return f"https://digilocker.gov.in/public/oauth2/1/authorize?client_id={self.client_id}&redirect_uri={redirect_uri}&response_type=code"
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[dict]:
        if not self.enabled:
            return self._mock_token_response(code)
        
        return None
    
    def get_user_info(self, access_token: str) -> Optional[dict]:
        if not self.enabled:
            return self._mock_user_info(access_token)
        
        return None
    
    def _mock_authorization_url(self, redirect_uri: str) -> str:
        return f"/mock/digilocker/authorize?redirect_uri={redirect_uri}"
    
    def _mock_token_response(self, code: str) -> dict:
        return {
            "access_token": f"mock_token_{code}",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    
    def _mock_user_info(self, access_token: str) -> dict:
        return {
            "digilocker_id": "MOCK123456",
            "name": "Mock User",
            "dob": "1990-01-01",
            "verified": True
        }

digilocker_adapter = DigiLockerAdapter()
