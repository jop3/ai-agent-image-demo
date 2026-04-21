# 🔄 n8n Voice-to-Image Workflow Setup Guide

Detta är en komplett guide för att sätta upp AI Voice-to-Image funktionaliteten i n8n med exakt samma funktioner som Python-implementationen.

## 📋 Översikt

Workflowet implementerar:
- ✅ **Whisper transkribering** med KBLab svenska modeller
- ✅ **Röstkommandon** ("skapa bild", "generera bild", etc.)
- ✅ **Automatisk generering** vid meningsavslut
- ✅ **Prompt-förbättring** med Gemini Free tier
- ✅ **Bildgenerering** med Gemini Paid tier
- ✅ **Rensa transkription** kommando

## 🚀 Installation

### 1. Importera Workflow

1. Öppna n8n
2. Klicka på "Import from File"
3. Välj `n8n-voice-to-image-workflow.json`
4. Klicka "Import"

### 2. Installera Nödvändiga Noder

Kontrollera att du har följande noder installerade i n8n:

```bash
# I n8n Community Nodes
@n8n/n8n-nodes-langchain
```

Eller installera manuellt:
1. Settings → Community Nodes
2. Sök efter `@n8n/n8n-nodes-langchain`
3. Klicka "Install"

### 3. Konfigurera API-nycklar

#### A) HuggingFace API (för Whisper)

1. Skapa konto på [HuggingFace](https://huggingface.co)
2. Gå till Settings → Access Tokens
3. Skapa en ny token med "read" permissions
4. I n8n:
   - Credentials → Add Credential
   - Välj "HuggingFace API"
   - Namnge: "HuggingFace API"
   - Lägg till din token

#### B) Google Gemini API (Free Tier)

1. Gå till [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Skapa en **FREE tier** API-nyckel
3. I n8n:
   - Credentials → Add Credential
   - Välj "Google Gemini API"
   - Namnge: "Google Gemini API (Free Tier)"
   - Lägg till din nyckel

#### C) Google Gemini API (Paid Tier)

1. Gå till [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Skapa en **PAID tier** API-nyckel (från ett projekt med billing aktiverat)
3. I n8n:
   - Credentials → Add Credential
   - Välj "Google Gemini API"
   - Namnge: "Google Gemini API (Paid Tier)"
   - Lägg till din nyckel

### 4. Konfigurera Whisper-noden

Öppna noden "Whisper Transcription (KBLab Swedish)" och verifiera inställningarna:

```json
{
  "model": "KBLab/kb-whisper-large",
  "language": "sv",
  "task": "transcribe",
  "options": {
    "beam_size": 5,
    "best_of": 5,
    "temperature": 0,
    "vad_filter": true,
    "vad_parameters": {
      "min_silence_duration_ms": 300,
      "speech_pad_ms": 400
    }
  }
}
```

**Tillgängliga KBLab-modeller:**
- `KBLab/kb-whisper-tiny` (57.7M - snabbast)
- `KBLab/kb-whisper-base` (99.1M)
- `KBLab/kb-whisper-small` (0.3B - balans)
- `KBLab/kb-whisper-medium` (0.8B - bra kvalitet)
- `KBLab/kb-whisper-large` (2B - bästa kvalitet) ⭐ **REKOMMENDERAT**

## 🎯 Workflow-komponenter

### Node 1: Webhook Trigger
- **Path:** `/webhook/voice-to-image`
- **Method:** POST
- **Accepterar:** Audio binary data ELLER JSON-kommandon

### Node 2: Convert Audio to Binary
- Konverterar inkommande audio till binärt format för Whisper

### Node 3: Whisper Transcription (KBLab Swedish)
- Transkriberar svensk audio med KBLab Whisper
- Optimerad för svensk språk med:
  - `beam_size: 5` - högre noggrannhet
  - `best_of: 5` - fler kandidater
  - `temperature: 0` - deterministisk output
  - `vad_filter: true` - Voice Activity Detection

### Node 4: Voice Command Detection
- Detekterar röstkommandon:
  - "skapa bild"
  - "generera bild"
  - "skapa en bild"
  - "generera en bild"
  - "gör en bild"
- Detekterar även meningsavslut (`.`, `!`, `?`, `:`, `;`)

### Node 5: Clean Text
- Tar bort röstkommandon från texten
- Bevarar resten av meningen för bildgenerering

### Node 6: Enhance Prompt (Gemini Free)
- Använder Gemini 2.0 Flash Exp (FREE tier)
- Konverterar svensk text till detaljerad engelsk bildprompt
- **Samma prompt som Python-versionen:**

```
Du är en expert på att skapa bildprompter för AI-bildgenerering.

Användaren sa: "{user_text}"

Skapa en detaljerad, visuell bildprompt på engelska som fångar essensen av vad användaren sa.
Om det är ett abstrakt koncept (som "AI agent är ett workflow"), gör det visuellt och metaforiskt.

Regler:
- Max 2-3 meningar
- Var specifik om visuella detaljer (färger, stil, komposition)
- Gör det intressant och professionellt
- Svara ENDAST med bildprompten, ingen annan text

Bildprompt:
```

### Node 7: Generate Image (Gemini Paid)
- Använder Gemini 2.5 Flash Image (PAID tier)
- Genererar 1 PNG-bild
- Model: `models/gemini-2.5-flash-image`

**Alternativa modeller:**
- `imagen-3.0-generate-002` (Imagen 3 - $0.03/bild)
- `imagen-4.0-generate-001` (Imagen 4 - högsta kvalitet)

### Node 8: Save Image
- Sparar bilden lokalt med timestamp
- Format: `image_{timestamp}.png`

### Node 9: Webhook Response
- Returnerar JSON till klienten:

```json
{
  "type": "image_generated",
  "image": "base64_encoded_image",
  "prompt": "Enhanced prompt used",
  "original_text": "Original user text"
}
```

### Node 10-11: Command Router & Clear Response
- Hanterar "clear_transcription" kommando
- Returnerar bekräftelse:

```json
{
  "type": "transcription_cleared",
  "message": "Transkription har rensats"
}
```

## 📡 API-användning

### Skicka Audio för Transkribering

```bash
curl -X POST http://your-n8n-instance/webhook/voice-to-image \
  -H "Content-Type: application/octet-stream" \
  --data-binary @audio.wav
```

### Manuell Bildgenerering

```bash
curl -X POST http://your-n8n-instance/webhook/voice-to-image \
  -H "Content-Type: application/json" \
  -d '{
    "type": "generate_image",
    "text": "En vacker solnedgång över havet"
  }'
```

### Rensa Transkription

```bash
curl -X POST http://your-n8n-instance/webhook/voice-to-image \
  -H "Content-Type: application/json" \
  -d '{
    "command": "clear_transcription"
  }'
```

## 🔧 Anpassningar

### Ändra Bildmodell

I noden "Generate Image (Gemini Paid)", ändra `model`-parametern:

```json
{
  "model": "imagen-3.0-generate-002",  // För Imagen 3
  // eller
  "model": "imagen-4.0-generate-001"   // För Imagen 4
}
```

### Justera Meningsdetektion

I noden "Voice Command Detection", lägg till fler villkor:

```json
{
  "conditions": {
    "string": [
      {
        "value1": "={{$json.transcription}}",
        "operation": "regex",
        "value2": "[.!?:;]\\s*$"  // Justera regex här
      }
    ]
  }
}
```

### Byt Whisper-modell

I noden "Whisper Transcription", ändra `model`:

```json
{
  "model": "KBLab/kb-whisper-medium",  // För mindre VRAM
  // eller
  "model": "KBLab/kb-whisper-large"    // För bästa kvalitet
}
```

## 🎨 Integrera med Frontend

Du kan använda samma HTML-frontend (`index.html`) men uppdatera WebSocket-URLen till din n8n webhook:

```javascript
// I index.html
const WS_URL = 'http://your-n8n-instance/webhook/voice-to-image';
```

## 🐛 Felsökning

### "Model not found"
- Kontrollera att du använder rätt modellnamn: `KBLab/kb-whisper-large`
- Verifiera HuggingFace credentials

### "Insufficient credits"
- Gemini Free tier har begränsningar
- Paid tier krävs för bildgenerering
- Kontrollera billing på Google Cloud

### "Audio format not supported"
- Säkerställ att audio är i WAV/MP3-format
- Sample rate: 16000 Hz
- Channels: 1 (mono)

## 📊 Prestanda

| Komponent | Tid | Kostnad |
|-----------|-----|---------|
| Whisper (large) | ~2-3s | Gratis |
| Prompt-förbättring | ~1-2s | Gratis (Free tier) |
| Bildgenerering | ~5-10s | ~$0.01/bild |
| **Total** | **~8-15s** | **~$0.01/bild** |

## 🔄 Jämförelse med Python-version

| Funktion | Python | n8n | Status |
|----------|--------|-----|--------|
| KBLab Whisper | ✅ | ✅ | Identisk |
| Röstkommandon | ✅ | ✅ | Identisk |
| Prompt-förbättring | ✅ | ✅ | Samma prompt |
| Bildgenerering | ✅ | ✅ | Samma API |
| Rensa transkription | ✅ | ✅ | Identisk |
| Real-time WebSocket | ✅ | ⚠️ | Kräver extra config |
| Lokal bildlagring | ✅ | ✅ | Identisk |

## 📚 Resurser

- [n8n Documentation](https://docs.n8n.io/)
- [KBLab Whisper Models](https://huggingface.co/KBLab)
- [Google Gemini API](https://ai.google.dev/gemini-api/docs)
- [HuggingFace API](https://huggingface.co/docs/api-inference/index)

## 💡 Tips

1. **Testa steg för steg:** Använd n8n's "Execute Node" för att testa varje nod separat
2. **Spara logs:** Aktivera "Save execution data" för debugging
3. **Monitera kostnader:** Gemini Paid tier debiteras per bild
4. **Optimera för hastighet:** Använd `kb-whisper-medium` istället för `large` om hastighet är viktigare än kvalitet

---

**Skapad:** 2024-11-24
**Version:** 1.0
**Kompatibel med:** n8n v1.0+, Python version v2.0
