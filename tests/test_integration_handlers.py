"""Focused tests for integration handlers and settings."""

import os
import unittest
from unittest import mock

from config.settings import Settings
from elevenlabs_handler import ElevenLabsHandler
from google_auth import GoogleAuthManager
from youtube_handler import YouTubeHandler


class IntegrationHandlersTestCase(unittest.TestCase):
    def test_settings_load_google_cloud_fields(self):
        with mock.patch.dict(
            os.environ,
            {
                "GOOGLE_CLOUD_PROJECT_ID": "project-123",
                "GOOGLE_OAUTH_CLIENT_SECRETS_FILE": "client_secret.json",
                "GOOGLE_SERVICE_ACCOUNT_FILE": "service-account.json",
                "GOOGLE_OAUTH_SCOPES": "scope-a,scope-b",
                "YOUTUBE_CHANNEL_ID": "@pwywm",
            },
            clear=False,
        ):
            settings = Settings()
            self.assertEqual(settings.GOOGLE_CLOUD_PROJECT_ID, "project-123")
            self.assertEqual(settings.GOOGLE_OAUTH_CLIENT_SECRETS_FILE, "client_secret.json")
            self.assertEqual(settings.GOOGLE_SERVICE_ACCOUNT_FILE, "service-account.json")
            self.assertEqual(settings.GOOGLE_OAUTH_SCOPES, "scope-a,scope-b")
            self.assertEqual(settings.YOUTUBE_CHANNEL_ID, "@pwywm")

    def test_google_auth_reads_scopes_from_env(self):
        with mock.patch.dict(
            os.environ, {"GOOGLE_OAUTH_SCOPES": "scope-1, scope-2 ,scope-3"}, clear=False
        ):
            manager = GoogleAuthManager()
            self.assertEqual(manager.scopes, ["scope-1", "scope-2", "scope-3"])

    def test_elevenlabs_handler_requires_api_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as error:
                ElevenLabsHandler()
            self.assertIn("ELEVENLABS_API_KEY", str(error.exception))

    def test_youtube_handler_channel_filter_for_handle(self):
        self.assertEqual(YouTubeHandler._channel_filters("@pwywm"), {"forHandle": "@pwywm"})
        self.assertEqual(YouTubeHandler._channel_filters("UC123"), {"id": "UC123"})


if __name__ == "__main__":
    unittest.main()
