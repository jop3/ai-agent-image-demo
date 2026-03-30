# 🎤 Elevate Avega

En interaktiv demo för föreläsningar där din röst automatiskt transkriberas och genererar AI-bilder i realtid med Gemini API.

## 🌟 Features

- **Lokal Speech-to-Text**: Använder Faster-Whisper med CUDA för snabb transkribering (optimerad för 12GB VRAM)
- **Smart mening-detektering**: AI känner automatiskt igen när du är färdig med en mening
- **Gemini 2.5 Flash Image / Imagen**: Googles kraftfulla bildgenereringsmodeller
- **Real-time webbgränssnitt**: Se transkriptionen och bilder live
- **Prompt-förbättring**: Gemini konverterar dina ord till detaljerade bildprompter

## 🎯 Workflow

1. **Prata** → Din röst spelas in
2. **Transkribering** → Faster-Whisper konverterar röst till text lokalt
3. **Smart detektering** → Systemet känner igen när du är färdig med en mening
4. **Prompt-förbättring** → Gemini API förbättrar din text till en bildprompt
5. **Bildgenerering** → Gemini 3 Pro Image skapar en bild
6. **Display** → Bilden visas direkt i webbläsaren

## 📋 Krav

### Hårdvara
- Windows-dator
- NVIDIA GPU med minst 12GB VRAM
- Mikrofon

### Mjukvara
- Python 3.8 eller senare
- CUDA Toolkit (för Whisper GPU-acceleration)
- Google Gemini API-nyckel

## 🚀 Installation

### 1. Klona/Ladda ner projektet

```bash
cd ai-agent-image-demo
```

### 2. Installera Python-dependencies

```bash
pip install -r requirements.txt
```

### 3. Konfigurera API-nycklar

Skapa en `.env` fil (kopiera från `.env.example`):

```bash
copy .env.example .env
```

Redigera `.env` och lägg till **båda** dina Gemini API-nycklar:

```
# Free tier - används för text-generering och prompt-förbättring
GEMINI_API_KEY_FREE=din_free_tier_api_nyckel_här

# Paid tier - krävs för bildgenerering
GEMINI_API_KEY_PAID=din_paid_tier_api_nyckel_här
```

**Varför två nycklar?**
- **FREE tier**: Fungerar för vanlig Gemini-textgenerering (prompt-förbättring)
- **PAID tier**: Krävs för bildgenerering med Gemini/Imagen modeller

**Hur får jag API-nycklar?**
1. Gå till https://aistudio.google.com/app/apikey
2. Logga in med ditt Google-konto
3. Skapa två API-nycklar (en för free tier, en för paid tier konto)
4. Kopiera och klistra in i `.env` filen

**Tips**: Om du har samma nyckel kan du använda samma för båda (men då måste den vara paid tier)

### 4. (Valfritt) Justera inställningar

I `.env` kan du justera:

- `WHISPER_MODEL`: Modellstorlek (tiny, base, small, medium, large-v3)
  - **Rekommenderat**: `small` eller `medium` för 12GB VRAM
- `IMAGE_MODEL`: Bildmodell
  - `gemini-2.5-flash-image` (snabbare, billigare)
  - `gemini-3.0-pro-image` (bättre kvalitet, Nano Banana Pro)
- `SILENCE_DURATION`: Hur länge paus innan mening anses färdig (sekunder)
- `MIN_SENTENCE_LENGTH`: Minsta antal tecken för en mening

## ▶️ Användning

### Snabbstart (Windows)

Dubbelklicka på:
- `start.bat` - Startar både backend och webserver

### Manuell start

**Starta backend (Terminal 1):**
```bash
python main.py
```

**Starta webserver (Terminal 2):**
```bash
python server.py
```

**Öppna webbläsaren:**
Gå till http://localhost:8000

### Under föreläsningen

1. Öppna http://localhost:8000 i Chrome/Edge
2. Klicka på "🎤 Starta Inspelning"
3. Ge mikrofon-behörighet
4. Börja prata!
5. När du pausar efter en mening kommer en bild att genereras automatiskt

**Tips:**
- Prata tydligt och avsluta meningar med punkt-paus
- Systemet känner automatiskt igen när du är färdig
- Varje bild sparas i mappen `generated_images/`

## 📁 Projektstruktur

```
ai-agent-image-demo/
├── main.py                 # Backend: STT + Gemini integration
├── server.py              # HTTP server för webbgränssnitt
├── index.html             # Webbgränssnitt
├── requirements.txt       # Python dependencies
├── .env.example          # Exempel på konfiguration
├── .env                  # Din konfiguration (skapa denna!)
├── start.bat             # Windows startskript
├── generated_images/     # Sparade bilder (skapas automatiskt)
└── README.md             # Denna fil
```

## 🛠️ Felsökning

### "GEMINI_API_KEY_FREE saknas i .env filen!"
→ Se till att du har skapat `.env` och lagt till båda API-nycklarna (FREE och PAID)

### "Kunde inte ladda Whisper modell"
→ Kontrollera att CUDA är installerat korrekt:
```bash
nvidia-smi
```

### "Kunde inte få tillgång till mikrofonen"
→ Ge Chrome/Edge behörighet till mikrofonen i webbläsarinställningar

### Ingen bild genereras
→ Kontrollera:
- API-nyckeln är korrekt
- Du har credits kvar på ditt Gemini-konto
- Titta i konsolen för felmeddelanden

### WebSocket-fel
→ Säkerställ att `main.py` körs innan du öppnar webbläsaren

## 💡 Exempel på användning

**Du säger:**
> "En AI agent är som ett workflow, med en smart motor som bestämmer när det är färdigt"

**Gemini förbättrar till:**
> "A sophisticated flowchart visualization with interconnected nodes representing an AI workflow, featuring a glowing central processing unit symbolizing the intelligent decision-making engine, rendered in a modern tech aesthetic with blue and purple gradients"

**→ Bild genereras och visas!**

## 🎨 Anpassa

### Ändra bildmodell

I `.env`:
```bash
# Gemini 2.5 Flash Image - Snabb och bra (Nano Banana)
IMAGE_MODEL=gemini-2.5-flash-image

# Imagen 3 - Högre kvalitet ($0.03/bild)
IMAGE_MODEL=imagen-3.0-generate-002

# Imagen 4 - Senaste och bästa kvalitet
IMAGE_MODEL=imagen-4.0-generate-001
```

**Tips**: `gemini-2.5-flash-image` är perfekt för demos och föreläsningar - snabb och gratis kvot!

### Justera känslighet

För att bilden ska genereras snabbare/långsammare efter att du pratat:

```bash
SILENCE_DURATION=1.0        # Kortare paus krävs
MIN_SENTENCE_LENGTH=5       # Kortare meningar accepteras
```

## 📊 Teknisk Stack

- **Backend**: Python 3.8+
- **STT**: Faster-Whisper (CUDA)
- **AI/Bildgenerering**: Google Gemini API (Gemini 3 Pro Image)
- **Kommunikation**: WebSockets
- **Frontend**: Vanilla JavaScript + HTML/CSS
- **Server**: Python HTTP Server

## 🔒 Säkerhet

- Kör **endast lokalt** - öppna inte för externa anslutningar
- Håll din `.env` fil privat (ingår i `.gitignore`)
- Dela aldrig din Gemini API-nyckel

## 📝 Licens

MIT License - Använd fritt för dina föreläsningar!

## 🤝 Support

Frågor eller problem? Kontrollera:
1. Att alla dependencies är installerade
2. Att `.env` är korrekt konfigurerad
3. Att CUDA fungerar (`nvidia-smi`)
4. Konsolloggar för felmeddelanden

---

**Skapad för AI-agent föreläsningar 🎓**

Lycka till med din presentation! 🚀
