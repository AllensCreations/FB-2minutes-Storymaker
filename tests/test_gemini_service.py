"""
Unit tests for Gemini Service (Settings & Speech-Script Reconciliation).
"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import gemini_service


class TestGeminiService(unittest.TestCase):

    def setUp(self):
        self.orig_env = gemini_service.ENV_PATH
        self.test_env = REPO_ROOT / ".env.test"
        gemini_service.ENV_PATH = self.test_env

    def tearDown(self):
        gemini_service.ENV_PATH = self.orig_env
        if self.test_env.exists():
            self.test_env.unlink()

    def test_settings_read_write(self):
        saved = gemini_service.write_env_settings("AIzaSyMockKey123", "gemini-3.8-flash")
        self.assertEqual(saved["gemini_api_key"], "AIzaSyMockKey123")
        self.assertEqual(saved["gemini_model"], "gemini-3.8-flash")

        read = gemini_service.read_env_settings()
        self.assertEqual(read["gemini_api_key"], "AIzaSyMockKey123")
        self.assertEqual(read["gemini_model"], "gemini-3.8-flash")

    @patch("gemini_service.call_gemini_api")
    def test_reconcile_and_align_speech(self, mock_call):
        mock_response = """{
            "reconciled_script": "This is a clean narration without scene numbers.",
            "scenes": [
                {"text": "First scene narration"},
                {"text": "Second scene narration"},
                {"text": "Third scene narration"}
            ],
            "cuts": [4.5, 9.2],
            "summary": "Clean speech alignment across 3 scenes."
        }"""
        mock_call.return_value = mock_response

        res = gemini_service.reconcile_and_align_speech(
            transcription="Um, first scene narration. Then, second scene narration. Finally, third scene.",
            script_text="Scene 1: First scene narration.\nScene 2: Second scene narration.\nScene 3: Third scene narration.",
            audio_duration=15.0,
            scene_count=3,
            api_key="mock_key",
            model="gemini-3.8-flash"
        )

        self.assertTrue(res["ok"])
        self.assertEqual(len(res["cuts"]), 2)
        self.assertEqual(res["cuts"][0], 4.5)
        self.assertEqual(res["cuts"][1], 9.2)
        self.assertIn("clean narration", res["reconciled_script"])

    def test_pcm_to_wav_bytes(self):
        # 16-bit mono 24kHz silence (4800 samples = 0.2s = 9600 bytes)
        raw_pcm = b"\x00" * 9600
        wav_bytes = gemini_service.pcm_to_wav_bytes(raw_pcm, sample_rate=24000)
        self.assertTrue(wav_bytes.startswith(b"RIFF"))
        self.assertIn(b"WAVE", wav_bytes[:12])
        self.assertGreater(len(wav_bytes), len(raw_pcm))

    @patch("gemini_service.call_gemini_audio_api")
    def test_generate_gemini_tts(self, mock_audio_api):
        # Return mock WAV bytes
        raw_pcm = b"\x00" * 4800
        mock_wav = gemini_service.pcm_to_wav_bytes(raw_pcm, sample_rate=24000)
        mock_audio_api.return_value = (mock_wav, "audio/wav")

        res = gemini_service.generate_gemini_tts(
            script_text="Scene 1: Once upon a time in a distant kingdom.\nScene 2: A baker worked with golden dough.",
            voice_name="Charon",
            api_key="mock_key"
        )

        self.assertTrue(res["ok"])
        self.assertEqual(res["voice"], "Charon")
        self.assertEqual(res["mime_type"], "audio/wav")
        self.assertIn("audio_base64", res)

    @patch("gemini_service.call_gemini_audio_api")
    def test_generate_gemini_tts_from_user_json(self, mock_audio_api):
        raw_pcm = b"\x00" * 4800
        mock_wav = gemini_service.pcm_to_wav_bytes(raw_pcm, sample_rate=24000)
        mock_audio_api.return_value = (mock_wav, "audio/wav")

        user_json = json.dumps({
            "Title": "The 'Validation' Addiction",
            "Caption": "What if applause keeps you prisoner?",
            "Description": "Build a life for yourself.",
            "script": [
                {"scene_number": 0, "narration": "What if you are always exhausted?"},
                {"scene_number": 1, "narration": "This is The Validation Trap."}
            ]
        })

        res = gemini_service.generate_gemini_tts(
            script_text=user_json,
            voice_name="Charon",
            api_key="mock_key"
        )
        self.assertTrue(res["ok"])
        # Verify the prompt passed to call_gemini_audio_api contains the pure narration, not the JSON braces or 'Please narrate'
        prompt_called = mock_audio_api.call_args[1]["prompt"]
        self.assertIn("What if you are always exhausted?", prompt_called)
        self.assertIn("This is The Validation Trap.", prompt_called)
        self.assertNotIn('"Title":', prompt_called)
        self.assertNotIn("Please narrate", prompt_called)
        self.assertNotIn("Scene", prompt_called)

    def test_generate_gemini_tts_missing_key(self):
        res = gemini_service.generate_gemini_tts(
            script_text="Testing without key",
            api_key="",
            voice_name="Kore"
        )
        # Should fail cleanly with MISSING_API_KEY when no env key exists
        if not gemini_service.read_env_settings()["gemini_api_key"]:
            self.assertFalse(res["ok"])
            self.assertEqual(res["code"], "MISSING_API_KEY")


if __name__ == "__main__":
    unittest.main()

