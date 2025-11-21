#!/usr/bin/env python3
"""
AI Agent Voice-to-Image Demo (CPU VERSION)
För Windows om CUDA/PyAV installation misslyckas
"""

import asyncio
import json
import os
import time
import base64
import io
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pyaudio
from faster_whisper import WhisperModel
from google import genai
from google.genai import types
from websockets.server import serve
from dotenv import load_dotenv

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

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

class VoiceToImageAgent:
    """Main agent handling voice transcription and image generation"""

    def __init__(self):
        print("🚀 Initialiserar AI Agent (CPU MODE)...")

        # Initialize Whisper model - CPU VERSION
        print(f"📝 Laddar Whisper modell ({WHISPER_MODEL}) på CPU...")
        print("⚠️  OBS: CPU-mode är långsammare än GPU!")
        self.whisper = WhisperModel(
            WHISPER_MODEL,
            device="cpu",          # CPU instead of CUDA
            compute_type="int8"    # int8 instead of float16
        )
        print("✅ Whisper laddad (CPU-mode)!")

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

        # Audio buffering (collect ~3 seconds before processing)
        self.audio_buffer = []
        self.buffer_duration = 3.0  # seconds
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

        enhancement_prompt = f"""Du är en expert på att skapa bildprompter för AI-bildgenerering.

Användaren sa: "{user_text}"

Skapa en detaljerad, visuell bildprompt på engelska som fångar essensen av vad användaren sa.
Om det är ett abstrakt koncept (som "AI agent är ett workflow"), gör det visuellt och metaforiskt.

Regler:
- Max 2-3 meningar
- Var specifik om visuella detaljer (färger, stil, komposition)
- Gör det intressant och professionellt
- Svara ENDAST med bildprompten, ingen annan text

Bildprompt:"""

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
        print(f"🎨 Genererar bild för: '{prompt}'")

        try:
            # Use different API methods based on model type
            if "imagen" in IMAGE_MODEL.lower():
                # Use Imagen API with PAID tier
                response = self.gemini_client_paid.models.generate_image(
                    model=IMAGE_MODEL,
                    prompt=prompt,
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
                response = self.gemini_client_paid.models.generate_content(
                    model=IMAGE_MODEL,
                    contents=[prompt]
                )

                # Extract image from response
                for part in response.parts:
                    if part.inline_data is not None:
                        image_data = part.inline_data.data

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
            image_data = await self.generate_image(enhanced_prompt)

            if image_data:
                # Convert to base64 for web display
                image_base64 = base64.b64encode(image_data).decode('utf-8')

                await self.broadcast({
                    "type": "image_generated",
                    "image": image_base64,
                    "prompt": enhanced_prompt,
                    "original_text": sentence
                })
            else:
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

    async def transcribe_audio_stream(self, websocket):
        """
        Handle real-time audio transcription from WebSocket
        """
        print("🎤 Startar transkribering...")

        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    # Audio data received - add to buffer
                    audio_chunk = np.frombuffer(message, dtype=np.int16)
                    self.audio_buffer.extend(audio_chunk)

                    # Process when buffer is large enough
                    if len(self.audio_buffer) >= self.samples_per_buffer:
                        # Convert to float32 for Whisper
                        audio_data = np.array(self.audio_buffer, dtype=np.float32) / 32768.0

                        # Transcribe with Whisper
                        segments, info = self.whisper.transcribe(
                            audio_data,
                            language="sv",
                            vad_filter=True,
                            vad_parameters=dict(
                                min_silence_duration_ms=500
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

                                # Check if sentence is complete
                                if self.is_sentence_complete(self.current_sentence):
                                    complete_sentence = self.current_sentence.strip()
                                    print(f"\n📝 Komplett mening: '{complete_sentence}'")

                                    # Process in background
                                    asyncio.create_task(self.process_sentence(complete_sentence))

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
                "message": "Ansluten till AI Agent (CPU Mode)"
            })

            await self.transcribe_audio_stream(websocket)

        except Exception as e:
            print(f"❌ WebSocket fel: {e}")
        finally:
            self.connected_clients.remove(websocket)
            print(f"🔌 Klient frånkopplad från {websocket.remote_address}")

    async def start_server(self):
        """Start the WebSocket server"""
        print(f"\n🌐 Startar WebSocket server på ws://{WS_HOST}:{WS_PORT}")

        async with serve(self.websocket_handler, WS_HOST, WS_PORT):
            print(f"✅ Server igång!")
            print(f"\n📖 Öppna http://{WS_HOST}:8000 i din webbläsare")
            print("🎤 Tryck Ctrl+C för att stoppa\n")
            print("⚠️  OBS: Kör i CPU-mode - transkribering kan vara långsammare!")

            await asyncio.Future()  # Run forever

async def main():
    """Main entry point"""
    print("=" * 60)
    print("🎯 AI Agent Voice-to-Image Demo (CPU VERSION)")
    print("=" * 60)

    agent = VoiceToImageAgent()
    await agent.start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Avslutar...")
