"""
Gemini API Service for Speech-Script Reconciliation and Cut Alignment.
Persists credentials to local .env and calls Gemini REST API.
"""

import base64
import io
import json
import logging
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("GeminiService")

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / ".env"
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TTS_MODEL = "gemini-3.8-flash-tts"


def read_env_settings() -> Dict[str, Any]:
    """Read Gemini API settings and offline mode from local .env or os.environ."""
    settings = {
        "gemini_api_key": "",
        "gemini_model": DEFAULT_MODEL,
        "offline_mode": False,
        "db_app_key": "",
        "db_app_secret": "",
        "db_refresh_token": "",
        "db_folder": "/Think with Tobi",
        "gas_url": ""
    }
    if ENV_PATH.exists():
        try:
            for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k == "GEMINI_API_KEY":
                    settings["gemini_api_key"] = v
                elif k == "GEMINI_MODEL":
                    settings["gemini_model"] = v
                elif k == "OFFLINE_MODE":
                    settings["offline_mode"] = v.lower() in ("true", "1", "yes")
                elif k == "DROPBOX_APP_KEY":
                    settings["db_app_key"] = v
                elif k == "DROPBOX_APP_SECRET":
                    settings["db_app_secret"] = v
                elif k == "DROPBOX_REFRESH_TOKEN":
                    settings["db_refresh_token"] = v
                elif k == "DROPBOX_FOLDER":
                    settings["db_folder"] = v
                elif k in ("GOOGLE_SHEET_URL", "GOOGLE_APPS_SCRIPT_URL", "GAS_URL"):
                    settings["gas_url"] = v
        except Exception:
            pass

    if not settings["gemini_api_key"]:
        settings["gemini_api_key"] = os.getenv("GEMINI_API_KEY", "")
    if not settings["gemini_model"]:
        settings["gemini_model"] = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    if not settings["offline_mode"]:
        settings["offline_mode"] = os.getenv("OFFLINE_MODE", "").lower() in ("true", "1", "yes")
    if not settings["db_app_key"]:
        settings["db_app_key"] = os.getenv("DROPBOX_APP_KEY", "")
    if not settings["db_app_secret"]:
        settings["db_app_secret"] = os.getenv("DROPBOX_APP_SECRET", "")
    if not settings["db_refresh_token"]:
        settings["db_refresh_token"] = os.getenv("DROPBOX_REFRESH_TOKEN", "")
    if not settings["db_folder"] or settings["db_folder"] == "/Think with Tobi":
        settings["db_folder"] = os.getenv("DROPBOX_FOLDER", "/Think with Tobi")
    if not settings["gas_url"]:
        settings["gas_url"] = os.getenv("GOOGLE_SHEET_URL") or os.getenv("GAS_URL", "")

    return settings


def write_env_settings(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    offline_mode: Optional[bool] = None,
    db_app_key: Optional[str] = None,
    db_app_secret: Optional[str] = None,
    db_refresh_token: Optional[str] = None,
    db_folder: Optional[str] = None,
    gas_url: Optional[str] = None
) -> Dict[str, Any]:
    """Safely persist Gemini, Dropbox, and Google Sheets settings into local .env."""
    current = read_env_settings()
    clean_key = current["gemini_api_key"] if api_key is None else str(api_key or "").strip()
    clean_model = current["gemini_model"] if model is None else (str(model or "").strip() or DEFAULT_MODEL)
    is_offline = current["offline_mode"] if offline_mode is None else bool(offline_mode)

    c_db_key = current["db_app_key"] if db_app_key is None else str(db_app_key or "").strip()
    c_db_secret = current["db_app_secret"] if db_app_secret is None else str(db_app_secret or "").strip()
    c_db_refresh = current["db_refresh_token"] if db_refresh_token is None else str(db_refresh_token or "").strip()
    c_db_folder = current["db_folder"] if db_folder is None else str(db_folder or "").strip()
    c_gas_url = current["gas_url"] if gas_url is None else str(gas_url or "").strip()

    tracked_keys = {
        "GEMINI_API_KEY": clean_key,
        "GEMINI_MODEL": clean_model,
        "OFFLINE_MODE": "true" if is_offline else "false",
        "DROPBOX_APP_KEY": c_db_key,
        "DROPBOX_APP_SECRET": c_db_secret,
        "DROPBOX_REFRESH_TOKEN": c_db_refresh,
        "DROPBOX_FOLDER": c_db_folder,
        "GOOGLE_SHEET_URL": c_gas_url
    }
    seen_keys = set()
    lines = []

    if ENV_PATH.exists():
        try:
            for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                matched = False
                for tk, tv in tracked_keys.items():
                    if stripped.startswith(f"{tk}=") or (tk == "GOOGLE_SHEET_URL" and stripped.startswith("GAS_URL=")):
                        lines.append(f'{tk}="{tv}"')
                        seen_keys.add(tk)
                        matched = True
                        break
                if not matched:
                    lines.append(line)
        except Exception:
            lines = []

    for tk, tv in tracked_keys.items():
        if tk not in seen_keys:
            lines.append(f'{tk}="{tv}"')

    ENV_PATH.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    for tk, tv in tracked_keys.items():
        os.environ[tk] = tv

    return {
        "gemini_api_key": clean_key,
        "gemini_model": clean_model,
        "offline_mode": is_offline,
        "db_app_key": c_db_key,
        "db_app_secret": c_db_secret,
        "db_refresh_token": c_db_refresh,
        "db_folder": c_db_folder,
        "gas_url": c_gas_url
    }


def call_gemini_api(
    prompt: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    system_instruction: Optional[str] = None
) -> str:
    """Execute raw REST request to Google Gemini generateContent endpoint."""
    cfg = read_env_settings()
    key = (api_key or cfg.get("gemini_api_key", "")).strip()
    mdl = (model or cfg.get("gemini_model", "")).strip() or DEFAULT_MODEL

    if not key:
        raise ValueError("Gemini API key is not configured. Please set it in Settings.")

    # Remove any leading models/ prefix if typed
    mdl = mdl.replace("models/", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={key}"

    payload: Dict[str, Any] = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.95,
            "responseMimeType": "application/json"
        }
    }

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            res_json = json.loads(body)
            candidates = res_json.get("candidates", [])
            if not candidates:
                raise ValueError("No response generated by Gemini model.")
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise ValueError("Empty response parts from Gemini.")
            return parts[0].get("text", "")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(err_msg)
            msg = err_json.get("error", {}).get("message", err_msg)
        except Exception:
            msg = err_msg
        raise RuntimeError(f"Gemini API Error ({e.code}): {msg}")
    except Exception as e:
        raise RuntimeError(f"Failed to communicate with Gemini API: {str(e)}")


def test_gemini_connection(
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """Test connectivity and key validity against Gemini."""
    cfg = read_env_settings()
    key = (api_key or cfg.get("gemini_api_key", "")).strip()
    mdl = (model or cfg.get("gemini_model", "")).strip() or DEFAULT_MODEL

    if not key:
        return {"ok": False, "error": "No API key provided."}

    try:
        text = call_gemini_api("Return JSON: {\"status\": \"ok\"}", api_key=key, model=mdl)
        return {"ok": True, "message": f"Successfully connected to Gemini ({mdl})!", "response": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def reconcile_and_align_speech(
    transcription: str,
    script_text: str,
    audio_duration: float,
    scene_count: int,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use Gemini to compare spoken voiceover transcription against the written story script,
    reconcile differences, and generate high-precision scene cut points.
    """
    clean_script = str(script_text or "").strip()
    clean_trans = str(transcription or "").strip()
    duration = float(audio_duration or 0.0)
    count = int(scene_count or 1)

    if duration <= 0:
        return {"ok": False, "error": "Audio duration must be greater than 0."}
    if count < 1:
        return {"ok": False, "error": "Scene count must be at least 1."}

    system_instruction = (
        "You are an elite video editor and speech-alignment director. "
        "Your task is to analyze a spoken audio transcription alongside a written story script. "
        "Reconcile differences between what the voice actor spoke and the script. "
        "Strip any 'Scene 1:', 'Scene 2:' prefixes so the story narration is clean. "
        f"Map the narrative across exactly {count} visual scene frames over a total audio duration of {duration:.2f} seconds. "
        f"Provide exactly {count - 1} transition cut timestamps in strictly ascending seconds. "
        "Output ONLY strict valid JSON matching the requested schema."
    )

    user_prompt = f"""
TOTAL AUDIO DURATION: {duration:.2f} seconds
TARGET SCENE COUNT: {count} scenes (require {count - 1} transition cuts)

WRITTEN STORY SCRIPT:
\"\"\"{clean_script}\"\"\"

SPOKEN AUDIO TRANSCRIPTION:
\"\"\"{clean_trans}\"\"\"

INSTRUCTIONS:
1. Reconcile what was spoken with what was written into a coherent, clean story narration without scene numbers.
2. Segment the narration into {count} scenes matching the pacing and pauses in the audio.
3. Calculate {count - 1} scene cut points in seconds (e.g. [3.4, 7.8, 12.1]) strictly between 0.0 and {duration:.2f}.
4. Return strict JSON:
{{
  "reconciled_script": "Full continuous narration without any Scene X labels",
  "scenes": [
    {{"text": "Clean narration text for scene 1"}},
    {{"text": "Clean narration text for scene 2"}}
  ],
  "cuts": [cut1, cut2, ...],
  "summary": "Brief explanation of speech cadence and reconciled words"
}}
"""

    try:
        raw_json = call_gemini_api(
            user_prompt,
            api_key=api_key,
            model=model,
            system_instruction=system_instruction
        )
        data = json.loads(raw_json)

        # Validate cuts
        raw_cuts = data.get("cuts", [])
        validated_cuts = []
        for c in raw_cuts:
            try:
                val = round(float(c), 2)
                if 0.1 < val < (duration - 0.1):
                    validated_cuts.append(val)
            except Exception:
                pass

        validated_cuts = sorted(list(set(validated_cuts)))

        # Fallback if cuts count doesn't match expected scene_count - 1
        if len(validated_cuts) != (count - 1) and count > 1:
            # If Gemini returned fewer or more cuts, ensure proper spacing
            step = duration / count
            validated_cuts = [round(step * i, 2) for i in range(1, count)]

        return {
            "ok": True,
            "reconciled_script": data.get("reconciled_script", clean_script),
            "scenes": data.get("scenes", []),
            "cuts": validated_cuts,
            "summary": data.get("summary", f"Aligned {count} scenes across {duration:.1f}s.")
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}


def pcm_to_wav_bytes(pcm_data: bytes, sample_rate: int = 24000, num_channels: int = 1, sample_width: int = 2) -> bytes:
    """Wraps raw 16-bit PCM audio in a valid RIFF WAV container."""
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    return wav_io.getvalue()


def call_gemini_audio_api(
    prompt: str,
    voice_name: str = "Charon",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    system_instruction: Optional[str] = None
) -> Tuple[bytes, str]:
    """
    Calls Google Gemini generateContent with responseModalities: ["AUDIO"]
    and prebuilt voice configuration. Returns (wav_bytes, mime_type).
    """
    cfg = read_env_settings()
    if cfg.get("offline_mode"):
        raise ValueError("OFFLINE_MODE_ACTIVE: Offline mode is currently enabled in Settings.")

    key = (api_key or cfg.get("gemini_api_key", "")).strip()
    if not key:
        raise ValueError("MISSING_API_KEY: Gemini API key is not configured. Please set it in Settings.")

    # Determine audio-capable model
    # Priority: explicitly passed model if audio/tts-capable, else GEMINI_TTS_MODEL env, else DEFAULT_TTS_MODEL ("gemini-3.8-flash-tts")
    req_model = (model or "").strip()
    if req_model and ("tts" in req_model.lower() or "live" in req_model.lower() or "audio" in req_model.lower()):
        mdl = req_model
    else:
        mdl = os.getenv("GEMINI_TTS_MODEL", DEFAULT_TTS_MODEL)

    valid_voices = {"Puck", "Charon", "Kore", "Fenrir", "Aoede"}
    clean_voice = voice_name.capitalize() if (voice_name and voice_name.capitalize() in valid_voices) else "Puck"

    def _do_request(target_model: str, use_system_instruction: bool) -> Tuple[bytes, str]:
        target_clean = target_model.replace("models/", "")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_clean}:generateContent?key={key}"
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": clean_voice
                        }
                    }
                }
            }
        }

        if use_system_instruction and system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            res_json = json.loads(body)
            candidates = res_json.get("candidates", [])
            if not candidates:
                raise ValueError("No response generated by Gemini model.")
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise ValueError("Empty response parts from Gemini.")

            audio_data_b64 = None
            mime_type = "audio/wav"

            for part in parts:
                inline = part.get("inlineData")
                if inline and inline.get("data"):
                    audio_data_b64 = inline.get("data")
                    mime_type = inline.get("mimeType", "audio/wav")
                    break

            if not audio_data_b64:
                raise ValueError("No audio data returned in Gemini response.")

            raw_audio_bytes = base64.b64decode(audio_data_b64)

            # Check if PCM format that needs WAV container
            if "pcm" in mime_type.lower() or not raw_audio_bytes.startswith(b"RIFF"):
                sample_rate = 24000
                m = re.search(r"rate=(\d+)", mime_type.lower())
                if m:
                    sample_rate = int(m.group(1))
                wav_bytes = pcm_to_wav_bytes(raw_audio_bytes, sample_rate=sample_rate)
                return wav_bytes, "audio/wav"
            else:
                return raw_audio_bytes, mime_type

    # Try initial call, with smart fallback if text-only model or developer instruction error is returned
    candidate_models = [mdl]
    for alt in [DEFAULT_TTS_MODEL, "gemini-3.8-flash-lite-tts"]:
        if alt not in candidate_models:
            candidate_models.append(alt)

    last_err = None
    for current_model in candidate_models:
        for use_sys_inst in [False, True]:  # Prioritize False because TTS models disallow systemInstruction
            try:
                return _do_request(current_model, use_sys_inst)
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode("utf-8", errors="replace")
                try:
                    err_json = json.loads(err_msg)
                    msg = err_json.get("error", {}).get("message", err_msg)
                except Exception:
                    msg = err_msg

                last_err = f"Gemini Audio API Error ({e.code}): {msg}"

                # If developer instruction not enabled, retry without system instruction
                if "Developer instruction is not enabled" in msg:
                    continue
                # If model only supports text output, break inner loop to try next audio model
                if "only supports text output" in msg or e.code == 404:
                    break
            except Exception as e:
                last_err = str(e)
                break

    raise ValueError(last_err or "Gemini Audio Request Failed")


def apply_audio_speed(wav_bytes: bytes, speed: float = 1.1) -> bytes:
    """Uses ffmpeg atempo filter to speed up or slow down WAV audio losslessly."""
    if abs(speed - 1.0) < 0.01 or not wav_bytes:
        return wav_bytes
    try:
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-i", "pipe:0", "-filter:a", f"atempo={speed:.2f}", "-f", "wav", "pipe:1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = proc.communicate(input=wav_bytes, timeout=15)
        if proc.returncode == 0 and out.startswith(b"RIFF"):
            return out
    except Exception as e:
        logger.warning(f"Failed to apply atempo speed filter via ffmpeg: {e}")
    return wav_bytes


def generate_gemini_tts(
    script_text: str,
    voice_name: str = "Puck",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    speed: float = 1.1
) -> Dict[str, Any]:
    """
    Synthesizes natural cinematic storybook voiceover from script text using Gemini TTS.
    Defaults to voice 'Puck' and speeds up output to 1.1x tempo for crisp storytelling.
    Returns base64-encoded WAV audio ready for browser Web Audio playback and timeline alignment.
    """
    clean_script = str(script_text or "").strip()
    if not clean_script:
        return {"ok": False, "error": "Script text is empty.", "code": "EMPTY_SCRIPT"}

    # If raw story JSON is passed, automatically extract pure narration texts
    if clean_script.startswith('{') or clean_script.startswith('['):
        try:
            data = json.loads(clean_script)
            if isinstance(data, dict):
                raw_list = data.get("script") or data.get("scenes") or data.get("story") or data.get("Script") or data.get("Scenes")
                if isinstance(raw_list, list):
                    narrations = []
                    for item in raw_list:
                        if isinstance(item, dict):
                            t = item.get("narration") or item.get("text") or item.get("script") or ""
                        else:
                            t = str(item)
                        if t:
                            narrations.append(t)
                    if narrations:
                        clean_script = "\n\n".join(narrations)
            elif isinstance(data, list):
                narrations = []
                for item in data:
                    if isinstance(item, dict):
                        t = item.get("narration") or item.get("text") or ""
                    else:
                        t = str(item)
                    if t:
                        narrations.append(t)
                if narrations:
                    clean_script = "\n\n".join(narrations)
        except Exception:
            pass

    # Format script for natural cinematic storytelling pacing:
    # 1. Strip scene numbers like "Scene 1:", "Scene 2 -", "[Scene 3]" and transition markers like "(Next image)"
    lines = clean_script.splitlines()
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        if not l or l.startswith("#"):
            continue
        # Strip stage direction markers like (Next image) or [Next image]
        if re.match(r'^[(\[]\s*(?:next\s+image|scene\s*\d+|transition|cut|image\s*\d+)[)\]]$', l, flags=re.IGNORECASE):
            continue
        # Strip leading scene numbers e.g. "Scene 1: Hello" -> "Hello"
        l = re.sub(r'^(scene\s*\d+\s*[:\-–—]?|\d+\.\s*)', '', l, flags=re.IGNORECASE).strip()
        # Also clean inline "(Next image)" markers
        l = re.sub(r'\(next\s+image\)', '', l, flags=re.IGNORECASE).strip()
        if l:
            cleaned_lines.append(l)

    # Pure narration text only - Gemini TTS models speak the prompt text verbatim
    pure_narration = "\n\n".join(cleaned_lines)
    if not pure_narration:
        pure_narration = clean_script

    try:
        wav_bytes, mime_type = call_gemini_audio_api(
            prompt=pure_narration,
            voice_name=voice_name or "Puck",
            api_key=api_key,
            model=model
        )

        # Apply 1.1x audio speed processing if requested
        if speed and abs(speed - 1.0) >= 0.01:
            wav_bytes = apply_audio_speed(wav_bytes, speed=speed)

        audio_b64 = base64.b64encode(wav_bytes).decode("ascii")

        return {
            "ok": True,
            "audio_base64": audio_b64,
            "mime_type": "audio/wav",
            "voice": voice_name or "Puck",
            "speed": speed,
            "script_word_count": len(clean_script.split()),
            "message": f"Successfully generated voiceover using Gemini voice '{voice_name or 'Puck'}' at {speed}x speed."
        }
    except Exception as e:
        err_str = str(e)
        code = "MISSING_API_KEY" if "MISSING_API_KEY" in err_str else ("OFFLINE_MODE" if "OFFLINE_MODE" in err_str else "TTS_ERROR")
        return {
            "ok": False,
            "error": err_str,
            "code": code
        }


def detect_audio_silences(audio_path_or_bytes: Any, noise_db: float = -32.0, min_duration: float = 0.20) -> List[Tuple[float, float]]:
    """Detect silence intervals (start_sec, end_sec) using FFmpeg silencedetect or wav analysis."""
    import tempfile
    import subprocess
    temp_file = None
    if isinstance(audio_path_or_bytes, (bytes, bytearray)):
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_file.write(audio_path_or_bytes)
        temp_file.close()
        target_path = temp_file.name
    else:
        target_path = str(audio_path_or_bytes)

    try:
        cmd = [
            "ffmpeg", "-y", "-i", target_path,
            "-af", f"silencedetect=noise={noise_db}dB:d={min_duration}",
            "-f", "null", "-"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        silences = []
        start = None
        for line in res.stderr.splitlines():
            if "silence_start:" in line:
                m = re.search(r"silence_start:\s*([\d\.]+)", line)
                if m:
                    start = float(m.group(1))
            elif "silence_end:" in line and start is not None:
                m = re.search(r"silence_end:\s*([\d\.]+)", line)
                if m:
                    end = float(m.group(1))
                    silences.append((start, end))
                    start = None
        return silences
    except Exception:
        return []
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass


def snap_timestamp_to_silence(target_t: float, silences: List[Tuple[float, float]], window_sec: float = 0.35) -> float:
    """Find the midpoint of the closest silence window within window_sec."""
    candidates = []
    for s_start, s_end in silences:
        mid = (s_start + s_end) / 2.0
        dist = abs(mid - target_t)
        if dist <= window_sec:
            candidates.append((dist, mid))
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return round(candidates[0][1], 2)
    return round(target_t, 2)


def align_audio_with_gemini_multimodal(
    audio_path_or_bytes: Any,
    scenes: List[Dict[str, Any]],
    audio_duration: float,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    High-precision scene cut alignment using Gemini multimodal audio analysis,
    with smart PCM/FFmpeg silence snapping within 300ms.
    Falls back gracefully to word-count proportion + silence snapping when offline or without key.
    """
    count = len(scenes)
    duration = float(audio_duration or 0.0)
    if count < 2 or duration <= 0.0:
        return {"ok": False, "error": "At least 2 scenes and positive audio duration required."}

    silences = detect_audio_silences(audio_path_or_bytes)

    # Prepare fallback cuts using word-count proportion
    def compute_fallback_cuts() -> List[float]:
        word_counts = []
        for s in scenes:
            txt = s.get("text") or s.get("narration") or s.get("script") or ""
            wc = max(1, len(txt.split()))
            word_counts.append(wc)
        tot_words = sum(word_counts)
        cuts = []
        accum = 0.0
        for wc in word_counts[:-1]:
            accum += (wc / tot_words) * duration
            snapped = snap_timestamp_to_silence(accum, silences, window_sec=0.35)
            # Ensure strictly between 0.2 and duration - 0.2
            snapped = max(0.2, min(duration - 0.2, snapped))
            cuts.append(snapped)
        # Ensure strictly ascending
        for i in range(1, len(cuts)):
            if cuts[i] <= cuts[i - 1]:
                cuts[i] = round(cuts[i - 1] + 1.0, 2)
        return cuts

    cfg = read_env_settings()
    is_offline = cfg.get("offline_mode", False)
    key = (api_key or cfg.get("gemini_api_key", "")).strip()

    if is_offline or not key:
        cuts = compute_fallback_cuts()
        return {
            "ok": True,
            "cuts": cuts,
            "method": "offline_silence_snapping",
            "message": f"Auto-aligned {count} scenes via speech cadence and silence detection ({'Offline Mode' if is_offline else 'No API Key'})."
        }

    # Use Gemini Multimodal
    try:
        import base64
        if isinstance(audio_path_or_bytes, (bytes, bytearray)):
            audio_bytes = bytes(audio_path_or_bytes)
        else:
            audio_bytes = Path(audio_path_or_bytes).read_bytes()

        # Identify mime type
        mime = "audio/wav"
        if audio_bytes[:3] == b"ID3" or audio_bytes[:2] in (b"\xff\xfb", b"\xff\xf3"):
            mime = "audio/mp3"
        elif audio_bytes[4:8] == b"ftyp":
            mime = "audio/m4a"

        audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

        # Format scenes breakdown for prompt
        scenes_text_lines = []
        for idx, sc in enumerate(scenes, 1):
            t = sc.get("text") or sc.get("narration") or sc.get("script") or f"Scene {idx}"
            scenes_text_lines.append(f"Scene {idx}: \"{t.strip()}\"")
        scenes_block = "\n".join(scenes_text_lines)

        system_instruction = (
            "You are an expert audio editor and speech timing engineer. "
            "You listen carefully to narration audio and locate exact transition timestamps between scenes. "
            "Output ONLY valid JSON."
        )

        user_prompt = f"""Listen to the attached audio ({duration:.2f} seconds).
Below are the {count} story scenes in spoken order:
{scenes_block}

Determine the {count - 1} transition timestamps in seconds where each scene finishes speaking and the next begins.
Timestamps must be strictly ascending numbers between 0.1 and {duration - 0.1:.2f}.

Output strictly valid JSON with no markdown formatting:
{{"cuts": [timestamp1, timestamp2, ...]}}
"""

        req_model = (model or cfg.get("gemini_model") or DEFAULT_MODEL).replace("models/", "")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{req_model}:generateContent?key={key}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"inlineData": {"mimeType": mime, "data": audio_b64}},
                        {"text": user_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json"
            },
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            }
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            res_json = json.loads(body)
            parts = res_json.get("candidates", [])[0].get("content", {}).get("parts", [])
            text_out = parts[0].get("text", "") if parts else ""
            parsed = json.loads(text_out)
            raw_cuts = parsed.get("cuts", [])

            validated = []
            for c in raw_cuts:
                try:
                    val = float(c)
                    if 0.1 < val < (duration - 0.1):
                        # Snap to micro-silence within 300ms
                        snapped = snap_timestamp_to_silence(val, silences, window_sec=0.30)
                        validated.append(snapped)
                except Exception:
                    pass

            validated = sorted(list(set(validated)))
            if len(validated) == count - 1:
                return {
                    "ok": True,
                    "cuts": validated,
                    "method": "gemini_multimodal_audio",
                    "message": f"Successfully auto-aligned {count} scenes with Gemini AI speech analysis."
                }
    except Exception as e:
        print(f"[Gemini Multimodal Align Warning] {e}, using pace fallback")

    # Fallback if Gemini failed or returned invalid cut count
    fallback_cuts = compute_fallback_cuts()
    return {
        "ok": True,
        "cuts": fallback_cuts,
        "method": "pace_silence_snapping_fallback",
        "message": f"Auto-aligned {count} scenes using speech cadence and silence snapping."
    }

