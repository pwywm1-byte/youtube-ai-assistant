"""Google authentication helpers for YouTube integrations."""

from __future__ import annotations

import json
import logging
import os
from typing import List, Optional


DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube",
]

logger = logging.getLogger(__name__)


class GoogleAuthManager:
    """Handle OAuth 2.0 and service account authentication flows."""

    def __init__(
        self,
        client_secrets_file: Optional[str] = None,
        token_file: Optional[str] = None,
        service_account_file: Optional[str] = None,
        scopes: Optional[List[str]] = None,
    ) -> None:
        self.client_secrets_file = client_secrets_file or os.getenv(
            "GOOGLE_OAUTH_CLIENT_SECRETS_FILE", "client_secret.json"
        )
        self.token_file = token_file or os.getenv("GOOGLE_OAUTH_TOKEN_FILE", "token.json")
        self.service_account_file = service_account_file or os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        self.scopes = scopes or self._scopes_from_env()

    @staticmethod
    def _scopes_from_env() -> List[str]:
        raw = os.getenv("GOOGLE_OAUTH_SCOPES", ",".join(DEFAULT_SCOPES))
        return [scope.strip() for scope in raw.split(",") if scope.strip()]

    def load_service_account_credentials(self, scopes: Optional[List[str]] = None):
        """Load service account credentials from file configured in environment."""
        from google.oauth2 import service_account

        account_file = self.service_account_file
        if not account_file:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE is not set.")
        if not os.path.exists(account_file):
            raise FileNotFoundError(f"Service account file not found: {account_file}")

        return service_account.Credentials.from_service_account_file(
            account_file, scopes=scopes or self.scopes
        )

    def get_oauth_credentials(self, scopes: Optional[List[str]] = None, open_browser: bool = False):
        """Run OAuth flow or refresh token and return OAuth credentials."""
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        selected_scopes = scopes or self.scopes
        credentials = None

        if os.path.exists(self.token_file):
            credentials = Credentials.from_authorized_user_file(self.token_file, selected_scopes)

        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                with open(self.token_file, "w", encoding="utf-8") as token:
                    token.write(credentials.to_json())
            except Exception as exc:
                logger.warning("OAuth token refresh failed; re-running OAuth flow: %s", exc, exc_info=True)
                credentials = None
        if not credentials or not credentials.valid:
            if not os.path.exists(self.client_secrets_file):
                raise FileNotFoundError(
                    f"OAuth client secrets file not found: {self.client_secrets_file}"
                )
            flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, selected_scopes)
            credentials = flow.run_local_server(port=0, open_browser=open_browser)
            with open(self.token_file, "w", encoding="utf-8") as token:
                token.write(credentials.to_json())

        return credentials

    @staticmethod
    def oauth_config_from_env() -> dict:
        """Build OAuth config dict from environment variables."""
        client_id = os.getenv("YOUTUBE_CLIENT_ID")
        client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")

        if not client_id or not client_secret:
            raise ValueError("YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET must be set.")

        return {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "project_id": project_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }

    def save_oauth_config(self, output_path: str) -> str:
        """Write OAuth config from environment to a local client secrets file."""
        config = self.oauth_config_from_env()
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=2)
        return output_path
