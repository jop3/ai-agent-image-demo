#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elevate Avega
Real-time voice transcription with AI-generated images using Gemini API
"""

import asyncio
import json
import os
import sys
import time
import base64
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configure logging FIRST to suppress websocket handshake errors
logging.basicConfig(level=logging.INFO)
logging.getLogger('websockets.server').setLevel(logging.CRITICAL)
logging.getLogger('websockets.protocol').setLevel(logging.CRITICAL)
logging.getLogger('websockets').setLevel(logging.CRITICAL)

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Add NVIDIA CUDA DLLs to PATH for faster-whisper GPU support
# This must be done BEFORE importing WhisperModel
try:
    import site
    dll_added = False
    dll_paths = []

    # Try both possible site-packages locations
    for site_path in site.getsitepackages():
        nvidia_path = Path(site_path) / "nvidia"
        if nvidia_path.exists():
            # Add both cuBLAS and cuDNN to DLL search path
            for lib_name in ["cublas", "cudnn"]:
                lib_bin_path = nvidia_path / lib_name / "bin"
                if lib_bin_path.exists():
                    # Add to both os.add_dll_directory AND system PATH
                    os.add_dll_directory(str(lib_bin_path))
                    dll_paths.append(str(lib_bin_path))
                    print(f"[OK] Added {lib_name} to DLL search path: {lib_bin_path}")
                    dll_added = True
            if dll_added:
                break

    # Also add to system PATH environment variable for ctranslate2
    if dll_paths:
        current_path = os.environ.get("PATH", "")
        os.environ["PATH"] = os.pathsep.join(dll_paths) + os.pathsep + current_path
        print(f"[OK] Added {len(dll_paths)} CUDA library paths to system PATH")

    if not dll_added:
        print("[INFO] NVIDIA CUDA libraries not found, will use CPU mode")
except Exception as e:
    print(f"[WARNING] Could not add CUDA libraries to path: {e}")
    print("  (Will try to use CPU mode if GPU fails)")

import numpy as np
import pyaudio
from faster_whisper import WhisperModel
from google import genai
from google.genai import types
import websockets
from dotenv import load_dotenv
from aiohttp import web
import tempfile

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY_FREE = os.getenv("GEMINI_API_KEY_FREE")
GEMINI_API_KEY_PAID = os.getenv("GEMINI_API_KEY_PAID")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
SILENCE_DURATION = float(os.getenv("SILENCE_DURATION", "1.5"))
MIN_SENTENCE_LENGTH = int(os.getenv("MIN_SENTENCE_LENGTH", "10"))
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-2.5-flash-image")
WS_HOST = os.getenv("WS_HOST", "localhost")
WS_PORT = int(os.getenv("WS_PORT", "8765"))
HTTP_PORT = int(os.getenv("HTTP_PORT", "8000"))
AUTO_GENERATE_INTERVAL = int(os.getenv("AUTO_GENERATE_INTERVAL", "60"))  # seconds

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

class VoiceToImageAgent:
    """Main agent handling voice transcription and image generation"""

    def __init__(self):
        print("🚀 Initialiserar AI Agent...")

        # Initialize Whisper model
        print(f"📝 Laddar Whisper modell ({WHISPER_MODEL})...")

        # Use KBLab Swedish models if specified, otherwise use standard models
        # KBLab models: KBLab/whisper-large-swedish, KBLab/whisper-medium-swedish, etc.
        if "KBLab" in WHISPER_MODEL or "kb-whisper" in WHISPER_MODEL.lower():
            # KBLab models from HuggingFace
            model_name = WHISPER_MODEL
            print(f"🇸🇪 Använder KBLab svensk Whisper-modell")
        else:
            # Standard Whisper models (small, medium, large, etc.)
            model_name = WHISPER_MODEL
            print(f"🌍 Använder standard Whisper-modell")

        self.whisper = WhisperModel(
            model_name,
            device="cuda",
            compute_type="float16"
        )
        print("✅ Whisper laddad!")

        # Initialize Gemini clients (separate for free and paid tiers)
        print("🤖 Kopplar upp mot Gemini API...")

        # Free tier client (for text/prompt enhancement)
        if not GEMINI_API_KEY_FREE:
            raise ValueError("GEMINI_API_KEY_FREE saknas i .env filen!")
        self.gemini_client_free = genai.Client(api_key=GEMINI_API_KEY_FREE)
        print("✅ Gemini Free Tier ansluten (text-generering)")

        # Paid tier client (for image generation)
        if not GEMINI_API_KEY_PAID:
            raise ValueError("GEMINI_API_KEY_PAID saknas i .env filen!")
        self.gemini_client_paid = genai.Client(api_key=GEMINI_API_KEY_PAID)
        print("✅ Gemini Paid Tier ansluten (bildgenerering)")

        # State management
        self.current_sentence = ""
        self.last_speech_time = None
        self.is_processing = False
        self.connected_clients = set()
        self.client_modes = {}  # Track mode per client (python or n8n)

        # Auto-generate timer
        self.auto_generate_interval = AUTO_GENERATE_INTERVAL
        self.last_auto_generate_time = time.time()
        self.auto_generate_enabled = True

        # Audio buffering (collect ~4 seconds before processing for better accuracy)
        self.audio_buffer = []
        self.buffer_duration = 4.0  # seconds
        self.samples_per_buffer = int(RATE * self.buffer_duration)

        # Create output directory
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected WebSocket clients"""
        if self.connected_clients:
            await asyncio.gather(
                *[client.send(json.dumps(message)) for client in self.connected_clients],
                return_exceptions=True
            )

    def is_sentence_complete(self, text: str) -> bool:
        """
        Smart detection of sentence completion
        Looks for:
        - Sentence ending punctuation
        - Minimum length
        - Silence duration
        """
        # Check for sentence ending
        has_ending = any(text.strip().endswith(p) for p in ['.', '!', '?', ':', ';'])

        # Check minimum length
        is_long_enough = len(text.strip()) >= MIN_SENTENCE_LENGTH

        # Check silence duration
        silence_elapsed = False
        if self.last_speech_time:
            silence_elapsed = (time.time() - self.last_speech_time) > SILENCE_DURATION

        return has_ending and is_long_enough and silence_elapsed

    async def enhance_prompt_for_image(self, user_text: str) -> str:
        """
        Use Gemini to convert user's sentence into a detailed image prompt
        """
        print(f"💭 Förbättrar prompt: '{user_text}'")

        # Check if user text already contains a theme modifier (from preset buttons)
        has_theme = any(keyword in user_text.lower() for keyword in ['sci-fi', 'cyberpunk', 'christmas', 'anime', 'watercolor', 'neon'])

        if has_theme:
            # User already specified style, use text as-is
            enhancement_prompt = f"""This is a detailed image generation prompt that includes specific style instructions.

Prompt: "{user_text}"

The prompt already contains style and theme information. Keep the style instructions exactly as specified. You may add minor visual details to enhance clarity, but preserve the theme and style completely.

Rules:
- Keep all theme/style modifiers intact
- Only add complementary visual details if needed
- Max 3 sentences total
- Respond ONLY with the enhanced image prompt in English

Image prompt:"""
        else:
            # Standard enhancement for voice transcription
            enhancement_prompt = f"""This is a one minute transcript from a person doing a lecture and demonstration of what AI-agents are and how they work.

Transcript: "{user_text}"

Find the most relevant part of this transcript related to AI-agents and create an image prompt from it. The resulting image will be shown to the audience, so it must be appropriate and not contain anything offensive.

If you can't find anything relevant to AI-agents, use the transcript text to create a fun image, but still appropriate.

Rules:
- Max 2-3 sentences
- Be specific about visual details (colors, style, composition)
- Make it interesting and professional
- If it's an abstract concept (like "AI agent is a workflow"), make it visual and metaphorical
- Respond ONLY with the image prompt in English, no other text

Image prompt:"""

        try:
            # Use FREE tier for prompt enhancement
            response = self.gemini_client_free.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=enhancement_prompt
            )

            enhanced_prompt = response.text.strip()
            print(f"✨ Förbättrad prompt: '{enhanced_prompt}'")
            return enhanced_prompt

        except Exception as e:
            print(f"⚠️ Kunde inte förbättra prompt: {e}")
            return user_text

    async def generate_image(self, prompt: str) -> Optional[bytes]:
        """
        Generate image using Gemini API
        Supports both Gemini 2.5 Flash Image and Imagen models
        """
        # Add aspect ratio to prompt for widescreen format
        widescreen_prompt = f"{prompt} Create in widescreen 16:9 landscape format."
        print(f"🎨 Genererar bild för: '{widescreen_prompt}'")

        try:
            # Use different API methods based on model type
            if "imagen" in IMAGE_MODEL.lower():
                # Use Imagen API with PAID tier
                response = self.gemini_client_paid.models.generate_image(
                    model=IMAGE_MODEL,
                    prompt=widescreen_prompt,
                    config=types.GenerateImageConfig(
                        number_of_images=1,
                        output_mime_type='image/png',
                    )
                )

                if response.generated_images:
                    # Get PIL Image and convert to bytes
                    pil_image = response.generated_images[0].image

                    # Save image
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = self.output_dir / f"image_{timestamp}.png"
                    pil_image.save(image_path)

                    # Convert to bytes for transmission
                    img_byte_arr = io.BytesIO()
                    pil_image.save(img_byte_arr, format='PNG')
                    image_data = img_byte_arr.getvalue()

                    print(f"✅ Bild genererad och sparad: {image_path}")
                    return image_data

            else:
                # Use Gemini 2.5 Flash Image (generate_content method) with PAID tier
                # Note: Aspect ratio controlled via prompt text, not API parameters
                response = self.gemini_client_paid.models.generate_content(
                    model=IMAGE_MODEL,
                    contents=[widescreen_prompt]
                )

                # Try different ways to access the image data
                image_data = None

                # Method 1: Try candidates[0].content.parts
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data is not None:
                                image_data = part.inline_data.data
                                break

                # Method 2: Try direct text attribute (if it's base64)
                if not image_data and hasattr(response, 'text'):
                    try:
                        # Might be base64 encoded
                        image_data = base64.b64decode(response.text)
                    except:
                        pass

                # Method 3: Check for generated_images attribute
                if not image_data and hasattr(response, 'generated_images') and response.generated_images:
                    pil_image = response.generated_images[0].image
                    img_byte_arr = io.BytesIO()
                    pil_image.save(img_byte_arr, format='PNG')
                    image_data = img_byte_arr.getvalue()

                if image_data:
                    # Save image locally
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = self.output_dir / f"image_{timestamp}.png"

                    with open(image_path, "wb") as f:
                        f.write(image_data)

                    print(f"✅ Bild genererad och sparad: {image_path}")
                    return image_data

            print("⚠️ Ingen bild i responsen")
            return None

        except Exception as e:
            print(f"❌ Fel vid bildgenerering: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def process_sentence(self, sentence: str):
        """
        Process a complete sentence: enhance prompt and generate image
        """
        if self.is_processing:
            print("⏳ Processar redan en mening, väntar...")
            return

        self.is_processing = True

        print(f"\n{'='*80}")
        print(f"🎨 BILDGENERERING INITIERAD")
        print(f"{'='*80}")
        print(f"📝 Mening: '{sentence}'")
        print(f"👥 Anslutna klienter: {len(self.connected_clients)}")
        print(f"🔧 Klient-lägen: {list(self.client_modes.values())}")
        print(f"{'='*80}\n")

        try:
            # Send status update
            await self.broadcast({
                "type": "processing",
                "sentence": sentence
            })

            # Step 1: Enhance the prompt
            enhanced_prompt = await self.enhance_prompt_for_image(sentence)

            await self.broadcast({
                "type": "prompt_enhanced",
                "original": sentence,
                "enhanced": enhanced_prompt
            })

            # Step 2: Generate image
            print("🖼️ Genererar bild med Gemini...")
            image_data = await self.generate_image(enhanced_prompt)

            if image_data:
                print(f"✅ Bild genererad! Storlek: {len(image_data)} bytes")

                # Convert to base64 for web display
                image_base64 = base64.b64encode(image_data).decode('utf-8')

                print(f"📤 Skickar bild till {len(self.connected_clients)} klienter...")
                await self.broadcast({
                    "type": "image_generated",
                    "image": image_base64,
                    "prompt": enhanced_prompt,
                    "original_text": sentence
                })

                print(f"{'='*80}")
                print(f"✨ BILDGENERERING SLUTFÖRD")
                print(f"{'='*80}\n")

                # Clear transcription after generating image
                await asyncio.sleep(1)  # Brief pause to show the result
                await self.broadcast({
                    "type": "clear_transcription"
                })
                print("🗑️ Transkription rensad efter bildgenerering")
            else:
                print("❌ Bildgenerering misslyckades!")
                await self.broadcast({
                    "type": "error",
                    "message": "Kunde inte generera bild"
                })

        except Exception as e:
            print(f"❌ Fel vid processning: {e}")
            await self.broadcast({
                "type": "error",
                "message": str(e)
            })
        finally:
            self.is_processing = False
            self.current_sentence = ""
            self.last_auto_generate_time = time.time()  # Reset timer after generation

    async def transcribe_audio_stream(self, websocket):
        """
        Handle real-time audio transcription from WebSocket
        """
        print("🎤 Startar transkribering...")

        try:
            async for message in websocket:
                # Handle JSON commands (like set_mode, clear_transcription, generate_image)
                if isinstance(message, str):
                    try:
                        data = json.loads(message)

                        if data.get('type') == 'set_mode':
                            # Set mode for this client
                            mode = data.get('mode', 'python')
                            self.client_modes[id(websocket)] = mode
                            print(f"\n{'='*80}")
                            print(f"🔄 LÄGESÄNDRING")
                            print(f"📍 Klient: {websocket.remote_address}")
                            print(f"🔧 Nytt läge: {mode.upper()}")
                            print(f"👥 Alla lägen nu: {list(self.client_modes.values())}")
                            print(f"{'='*80}\n")

                        elif data.get('type') == 'clear_transcription':
                            # Clear transcription state
                            self.current_sentence = ""
                            self.last_speech_time = None
                            self.audio_buffer = []
                            print("🗑️ Transkription rensad på servern")

                            await self.broadcast({
                                "type": "transcription_cleared",
                                "message": "Transkription har rensats"
                            })

                        elif data.get('type') == 'generate_image':
                            # Manual image generation trigger
                            text = data.get('text', '').strip()
                            if text:
                                print(f"🎨 Manuell bildgenerering begärd för: '{text}'")
                                # Process in background
                                asyncio.create_task(self.process_sentence(text))
                            else:
                                print("⚠️ Ingen text att generera bild från")

                    except json.JSONDecodeError:
                        print(f"⚠️ Kunde inte parsa meddelande: {message}")
                    continue

                if isinstance(message, bytes):
                    # Audio data received - add to buffer
                    audio_chunk = np.frombuffer(message, dtype=np.int16)
                    self.audio_buffer.extend(audio_chunk)

                    # Process when buffer is large enough
                    if len(self.audio_buffer) >= self.samples_per_buffer:
                        # Convert to float32 for Whisper
                        audio_data = np.array(self.audio_buffer, dtype=np.float32) / 32768.0

                        # Transcribe with Whisper - optimized for accuracy
                        segments, info = self.whisper.transcribe(
                            audio_data,
                            language="sv",
                            beam_size=5,  # Higher beam size for better accuracy
                            best_of=5,    # Consider more candidates
                            temperature=0.0,  # Deterministic, more conservative output
                            vad_filter=True,
                            vad_parameters=dict(
                                min_silence_duration_ms=300,  # More sensitive to pauses
                                speech_pad_ms=400  # Add padding around speech
                            )
                        )

                        # Process segments
                        for segment in segments:
                            text = segment.text.strip()

                            if text:
                                self.current_sentence += " " + text
                                self.last_speech_time = time.time()

                                # Send transcription update
                                await self.broadcast({
                                    "type": "transcription",
                                    "text": self.current_sentence.strip()
                                })

                                # Check for voice commands
                                # Only respond to voice commands in Python mode
                                client_mode = self.client_modes.get(id(websocket), 'python')
                                current_text_lower = self.current_sentence.strip().lower()
                                voice_triggers = ["skapa bild", "generera bild", "skapa en bild", "generera en bild", "gör en bild"]

                                if any(trigger in current_text_lower for trigger in voice_triggers):
                                    if client_mode == 'python':
                                        # Extract text before the trigger command
                                        text_to_process = self.current_sentence.strip()
                                        for trigger in voice_triggers:
                                            # Remove the trigger phrase from the text
                                            if trigger in current_text_lower:
                                                # Case-insensitive removal
                                                import re
                                                text_to_process = re.sub(re.escape(trigger), '', text_to_process, flags=re.IGNORECASE).strip()
                                                break

                                        if text_to_process:
                                            print(f"\n{'='*80}")
                                            print(f"🎤 TRIGGER: RÖSTKOMMANDO (Python mode)")
                                            print(f"📝 Text: '{text_to_process}'")
                                            print(f"{'='*80}")
                                            # Process in background
                                            asyncio.create_task(self.process_sentence(text_to_process))
                                        else:
                                            print("⚠️ Röstkommando detekterat men ingen text att generera från")
                                    else:
                                        print(f"\n⏭️ IGNORERAT: Röstkommando i n8n mode: '{current_text_lower}'")

                                # Check if sentence is complete (automatic trigger)
                                # Only auto-generate in Python mode, not in n8n mode
                                elif self.is_sentence_complete(self.current_sentence):
                                    client_mode = self.client_modes.get(id(websocket), 'python')

                                    if client_mode == 'python':
                                        complete_sentence = self.current_sentence.strip()
                                        print(f"\n{'='*80}")
                                        print(f"⏸️ TRIGGER: PAUS DETEKTERAD (Python mode)")
                                        print(f"📝 Mening: '{complete_sentence}'")
                                        print(f"⏱️ Tystnad: >{SILENCE_DURATION}s")
                                        print(f"{'='*80}")

                                        # Process in background
                                        asyncio.create_task(self.process_sentence(complete_sentence))
                                    else:
                                        print(f"\n⏭️ IGNORERAT: Paus i n8n mode (text: '{self.current_sentence.strip()}')")

                        # Clear processed buffer, keep last 0.5s for overlap
                        overlap_samples = int(RATE * 0.5)
                        self.audio_buffer = self.audio_buffer[-overlap_samples:]

        except Exception as e:
            print(f"❌ Transkriberingfel: {e}")

    async def websocket_handler(self, websocket):
        """Handle WebSocket connections"""
        print(f"🔌 Ny klient ansluten från {websocket.remote_address}")
        self.connected_clients.add(websocket)

        try:
            await self.broadcast({
                "type": "connected",
                "message": "Ansluten till AI Agent"
            })

            await self.transcribe_audio_stream(websocket)

        except websockets.exceptions.ConnectionClosedOK:
            # Normal disconnect, no need to log
            pass
        except websockets.exceptions.ConnectionClosedError as e:
            # Only log if it's an unexpected error
            if "1000" not in str(e):  # 1000 = normal closure
                print(f"⚠️ Klient förlorade anslutningen: {websocket.remote_address}")
        except Exception as e:
            print(f"❌ WebSocket fel: {e}")
        finally:
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)
            # Remove mode tracking for this client
            client_id = id(websocket)
            if client_id in self.client_modes:
                del self.client_modes[client_id]
            print(f"🔌 Klient frånkopplad från {websocket.remote_address}")

    async def transcribe_text_api(self, request):
        """HTTP API endpoint för texttranskribering (simulerad för n8n)"""
        try:
            data = await request.json()
            text = data.get('text', '')

            if not text:
                return web.json_response({
                    'error': 'No text provided'
                }, status=400)

            print(f"📝 API transkribering: '{text}'")

            return web.json_response({
                'success': True,
                'transcription': text,
                'language': 'sv',
                'model': 'KBLab/kb-whisper-large',
                'confidence': 0.95
            })

        except Exception as e:
            print(f"❌ API fel: {e}")
            return web.json_response({
                'error': str(e)
            }, status=500)

    async def transcribe_audio_api(self, request):
        """HTTP API endpoint för audiotranskribering (riktig Whisper)"""
        try:
            # Ta emot audio-fil
            reader = await request.multipart()
            audio_data = None

            async for part in reader:
                if part.name == 'audio':
                    audio_data = await part.read()
                    break

            if not audio_data:
                return web.json_response({
                    'error': 'No audio file provided'
                }, status=400)

            print(f"🎤 API audio transkribering ({len(audio_data)} bytes)")

            # Spara temporärt - låt Whisper/ffmpeg hantera formatet
            # Använd .webm eftersom det är vad vi får från browsern
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name

            try:
                print(f"📁 Temp file: {tmp_path}")

                # Använd samma Whisper-modell som live-demon
                # Whisper använder ffmpeg under huven och kan hantera webm
                segments, info = self.whisper.transcribe(
                    tmp_path,
                    language="sv",
                    beam_size=5,
                    best_of=5,
                    temperature=0.0
                )

                transcription = " ".join([seg.text.strip() for seg in segments])

                print(f"✅ Transkriberat: '{transcription}'")

                return web.json_response({
                    'success': True,
                    'transcription': transcription,
                    'language': info.language,
                    'model': 'KBLab/kb-whisper-large',
                    'confidence': info.language_probability
                })

            finally:
                # Rensa temporär fil
                os.unlink(tmp_path)

        except Exception as e:
            print(f"❌ Audio API fel: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'error': str(e)
            }, status=500)

    async def start_http_server(self):
        """Start HTTP API server för n8n integration"""
        app = web.Application()

        # Serve static HTML files
        async def serve_html(request):
            filename = request.match_info.get('filename', 'index.html')

            # Add .html if not already present
            if not filename.endswith('.html'):
                filename = filename + '.html'

            filepath = Path(__file__).parent / filename

            if filepath.exists() and filepath.suffix == '.html':
                return web.FileResponse(filepath)
            else:
                raise web.HTTPNotFound()

        # Routes - ORDER MATTERS! More specific routes first
        # API endpoints (most specific)
        app.router.add_post('/api/transcribe/text', self.transcribe_text_api)
        app.router.add_post('/api/transcribe/audio', self.transcribe_audio_api)
        app.router.add_get('/api/health', lambda r: web.json_response({'status': 'ok'}))

        # HTML files
        app.router.add_get('/', lambda r: web.FileResponse(Path(__file__).parent / 'index.html'))
        app.router.add_get('/{filename}', serve_html)  # Catch-all for HTML (least specific)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, WS_HOST, HTTP_PORT)
        await site.start()

        print(f"🌐 HTTP API server igång på http://{WS_HOST}:{HTTP_PORT}")
        print(f"   📝 Text: POST http://{WS_HOST}:{HTTP_PORT}/api/transcribe/text")
        print(f"   🎤 Audio: POST http://{WS_HOST}:{HTTP_PORT}/api/transcribe/audio")

    async def auto_generate_loop(self):
        """Background task that auto-generates images based on accumulated transcription"""
        print(f"⏰ Auto-generate aktiverad: var {self.auto_generate_interval}s")

        while True:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds

                # Check if enough time has passed and we have text
                current_time = time.time()
                time_since_last = current_time - self.last_auto_generate_time

                # Only auto-generate if we have connected clients in Python mode
                has_python_client = any(
                    mode == 'python'
                    for mode in self.client_modes.values()
                )

                if (self.auto_generate_enabled and
                    has_python_client and  # Only if someone is in Python mode
                    time_since_last >= self.auto_generate_interval and
                    self.current_sentence.strip() and
                    not self.is_processing):

                    print(f"\n{'='*80}")
                    print(f"⏰ TRIGGER: AUTO-GENERATE TIMER")
                    print(f"⏱️ Tid sedan senaste: {int(time_since_last)}s (intervall: {self.auto_generate_interval}s)")
                    print(f"📝 Ackumulerad text: '{self.current_sentence.strip()}'")
                    print(f"{'='*80}")
                    await self.process_sentence(self.current_sentence)

            except Exception as e:
                print(f"❌ Fel i auto-generate loop: {e}")

    async def start_server(self):
        """Start both WebSocket and HTTP servers"""
        print(f"\n🌐 Startar servrar...")

        # Start HTTP API server
        await self.start_http_server()

        # Custom process_request to handle handshake errors silently
        async def process_request(path, request_headers):
            # Accept all connections, let the handler deal with errors
            return None

        # Start WebSocket server
        async with websockets.serve(
            self.websocket_handler,
            WS_HOST,
            WS_PORT,
            process_request=process_request
        ):
            print(f"🌐 WebSocket server igång på ws://{WS_HOST}:{WS_PORT}")
            print(f"\n✅ Alla servrar igång!")
            print(f"\n📖 För live-demo: http://{WS_HOST}:{HTTP_PORT}")
            print(f"🔌 För n8n: http://{WS_HOST}:{HTTP_PORT}/api/transcribe/text")
            print("🎤 Tryck Ctrl+C för att stoppa\n")

            # Start auto-generate background task
            asyncio.create_task(self.auto_generate_loop())

            await asyncio.Future()  # Run forever

async def main():
    """Main entry point"""
    print("=" * 60)
    print("🎯 Elevate Avega")
    print("=" * 60)

    agent = VoiceToImageAgent()
    await agent.start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Avslutar...")
