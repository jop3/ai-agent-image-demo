# 🎤 Elevate Avega - Presentation Cheat Sheet

## 🚀 Quick Start Commands

```bash
# Terminal 1: Start Python API + WebSocket Server
python main.py

# Terminal 2: Start n8n (if not already running)
n8n start

# Terminal 3: Serve Frontend (optional - or just open index.html)
python -m http.server 8080
```

## 📋 System Overview

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Browser UI    │──────│  Python API      │──────│  KBLab Whisper  │
│  (index.html)   │      │  (port 8000)     │      │  (local model)  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
         │
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    n8n Workflow                              │
│  (port 5678/webhook/voice-to-image-ai)                      │
│                                                              │
│  1. Webhook → 2. Whisper → 3. Detection → 4. 🤖 Gemini AI  │
│  → 5. 🤖 Gemini AI Image → 6. Save → 7. Response           │
│                                                              │
│  ✨ Uses native AI nodes instead of HTTP requests!          │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Two Workflow Options

You have **two workflow files** to choose from:

### Option 1: AI Nodes (RECOMMENDED) 🌟
**File:** `n8n-demo-workflow-presentation-ai-nodes.json`
- ✅ Uses n8n's native **Google Gemini AI nodes**
- ✅ Cleaner, more visual
- ✅ Better for demonstrations
- ✅ Easier credential management
- ✅ Shows "AI-powered workflow" explicitly

### Option 2: HTTP Requests (Fallback)
**File:** `n8n-demo-workflow-presentation.json`
- Uses generic HTTP Request nodes
- More manual configuration
- Good if AI nodes aren't available in your n8n version

**This cheat sheet covers the AI Nodes version!**
See `N8N_AI_NODES_SETUP.md` for detailed setup.

## 🎯 Key Demo Points

### 1. **KBLab Swedish Whisper** (Main Differentiator)
- Model: `KBLab/kb-whisper-large`
- Why: Swedish government-funded, optimized for Swedish language
- Comparison: Far superior to standard Whisper for Swedish text
- Demo phrase: "En vacker solnedgång över Stockholms skärgård"

### 2. **Dual API Keys Strategy**
- **Free Tier** (Gemini 2.0 Flash Exp): Text enhancement
- **Paid Tier** (Gemini 2.5 Flash Image): Image generation (~$0.01/image)
- Why: Cost optimization - only pay for expensive operations

### 3. **Voice Command Detection**
- Triggers: "skapa bild", "generera bild", "gör en bild"
- Alternative: End sentence with punctuation (. ! ? : ;)
- Smart cleanup: Removes voice commands from actual prompt

### 4. **Real-time vs Workflow Modes**
- **Python Mode**: Real-time streaming, instant feedback
- **n8n Mode**: Record → Process → Generate (better for demos)

## 📝 Presentation Flow (35 minutes)

### Part 1: Python Demo (10 minutes)

**Opening Statement:**
> "Idag ska jag visa er en AI-agent som omvandlar svensk röst till bilder i realtid, med hjälp av KBLab's svenska språkmodeller och n8n workflow automation."

**Demo Steps:**
1. **Open Browser** → `http://localhost:8080`
2. **Show UI** → Point out mode selector (Python vs n8n)
3. **Start Recording** → Click "🎤 Starta Inspelning"
4. **Say Test Phrase:**
   - Swedish: "En majestätisk norrsken över svenska fjällen"
   - Wait for transcription to appear
5. **Show Transcription** → Point out KBLab model detection
6. **Trigger Generation:**
   - Say: "Skapa bild" OR
   - Say: "En vacker solnedgång över havet."
7. **Watch Progress:**
   - Whisper transcription
   - Gemini prompt enhancement
   - Image generation
8. **Show Result** → Image appears in right panel

**Key Points to Mention:**
- ✅ Local Whisper model (no cloud dependency)
- ✅ Swedish-optimized (KBLab)
- ✅ Real-time processing
- ✅ WebSocket communication

### Part 2: n8n Workflow (25 minutes)

**Switch to n8n Mode:**
1. Click "📦 n8n Workflow Mode" button
2. Explain: "Now using workflow automation instead of direct Python"

**n8n Workflow Demonstration:**
1. **Open n8n** → `http://localhost:5678`
2. **Import Workflow:**
   - Click "Import from File"
   - Select `n8n-demo-workflow-presentation.json`
3. **Show Workflow Structure:**
   ```
   1. INPUT: Webhook
   2. WHISPER: Transkribering (calls Python API)
   3. DETEKTION: Röstkommandon (JavaScript)
   4. GEMINI FREE: Förbättra Prompt
   5. GEMINI PAID: Generera Bild
   6. Extrahera Bild
   7. Spara Bild
   8. OUTPUT: Response
   ```

**Step-by-Step Walkthrough:**

**Node 1: 🎤 Webhook**
- **PAUSE HERE** ⏸️
- Show webhook URL: `/webhook/voice-to-image`
- Explain: "Receives text from frontend"
- Test: Click "Execute Workflow" (will wait for webhook call)

**Node 2: 📝 Whisper Transkribering**
- **PAUSE HERE** ⏸️
- Show API call: `http://localhost:8000/api/transcribe/text`
- Explain: "Calls our local Python API with KBLab Whisper"
- Point out input handling: `$json.text || $json.body.text || ...`

**EXECUTE UP TO HERE:**
1. Go back to browser
2. Record voice: "En vacker solnedgång"
3. Stop recording
4. Go back to n8n
5. **Click on "👁️ VISA: Whisper Output" node**
6. Show output:
   ```json
   {
     "📝 TRANSKRIBERAD TEXT": "En vacker solnedgång",
     "🤖 MODELL": "KBLab/kb-whisper-large",
     "🌍 SPRÅK": "sv"
   }
   ```

**Node 3: 🎯 Röstkommando-detektion**
- **PAUSE HERE** ⏸️
- Show JavaScript code
- Explain detection logic:
  ```javascript
  const voiceTriggers = [
    'skapa bild',
    'generera bild',
    'gör en bild'
  ];
  ```
- Point out text cleaning

**Node 4: 👁️ VISA: Detektion Results**
- **PAUSE HERE** ⏸️
- Show before/after:
  ```json
  {
    "📄 ORIGINAL": "Skapa bild av en vacker solnedgång",
    "✨ RENSAD TEXT": "en vacker solnedgång",
    "🎤 KOMMANDO DETEKTERAT?": "✅ JA"
  }
  ```

**Node 5: 💡 Förbättra Prompt (Gemini Free)**
- **PAUSE HERE** ⏸️
- Show prompt engineering:
  ```
  Du är en expert på bildprompter.
  Användaren sa: "en vacker solnedgång"
  Skapa en detaljerad bildprompt på engelska.

  Regler:
  - Max 2-3 meningar
  - Beskriv färger, stil, komposition
  - Gör det visuellt intressant
  ```
- Explain: "Free tier API, no cost"

**Node 6: 👁️ VISA: Prompt Enhancement**
- **PAUSE HERE** ⏸️
- Show transformation:
  ```json
  {
    "🇸🇪 SVENSK INPUT": "en vacker solnedgång",
    "🇬🇧 ENGELSK PROMPT": "A breathtaking sunset over calm waters,
                           with vibrant orange and pink hues reflecting
                           off gentle waves, silhouetted sailboats in
                           the distance, cinematic composition",
    "📊 FÖRBÄTTRING": "Från simpel text → Detaljerad bildprompt"
  }
  ```

**Node 7: 🎨 Generera Bild (Gemini Paid)**
- **PAUSE HERE** ⏸️
- Explain: "Paid tier, ~$0.01 per image"
- Show model: `gemini-2.5-flash-image`
- Click "Execute Node"
- **Wait for generation (10-15 seconds)**

**Node 8: 📷 Extrahera Bild**
- **PAUSE HERE** ⏸️
- **IMPORTANT**: Click "Binary" tab (not "Table" or "JSON")
- Show generated image in n8n UI!
- Point out:
  - Image visible directly in workflow
  - Filename with timestamp
  - File size in KB

**Node 9: 💾 Spara Bild**
- Show save location: `generated_images/image_TIMESTAMP.png`
- Open folder to show saved file

**Node 10: ✅ Response**
- Show final JSON response structure
- Explain: Returns to browser with base64 image

## 🎨 Demo Phrases (Tested & Work Well)

### Swedish Landscapes:
- "En vacker solnedgång över Stockholms skärgård"
- "En majestätisk norrsken över svenska fjällen"
- "Ett mysigt rött torp vid en sjö i Dalarna"

### Swedish Culture:
- "En traditionell midsommarstång med blommor"
- "En fika med kanelbullar och kaffe"
- "En vikingaskepp på Östersjön"

### Abstract/Technical:
- "En AI-agent som ett flödesdiagram"
- "Framtidens teknik i Sverige"
- "Ett modernt kontorslandskap i Stockholm"

## 🔧 Troubleshooting Quick Fixes

### Issue: "Mikrofonen går inte att komma åt"
**Fix:** Check browser permissions (chrome://settings/content/microphone)

### Issue: "n8n workflow körs inte"
**Fix:**
1. Check webhook is active: `http://localhost:5678/webhook/voice-to-image`
2. Verify workflow is activated (toggle in top-right)
3. Check Python API is running: `http://localhost:8000/api/transcribe/text`

### Issue: "Ingen bild genereras"
**Fix:**
1. Check Gemini API keys in n8n credentials
2. Verify paid tier key has credits
3. Check node output for error messages

### Issue: "Fel språk transkriberas"
**Fix:**
- Ensure using KBLab model (check .env: `WHISPER_MODEL=KBLab/kb-whisper-large`)
- Check Whisper API response shows `"language": "sv"`

## 💡 Q&A Preparation

**Q: Varför KBLab och inte standard Whisper?**
> KBLab är tränad på svenska myndighetsdata och är betydligt bättre på svenska ord, namn och uttryck. Standard Whisper tränas främst på engelska data.

**Q: Varför två olika Gemini API-nycklar?**
> Kostnadoptimering! Prompt-förbättring är gratis (text-only), men bildgenerering kostar ~$0.01 per bild. Genom att separera dessa kan vi hålla nere kostnaderna.

**Q: Kan man använda andra bildmodeller?**
> Ja! Du kan byta ut Gemini mot DALL-E, Midjourney API, Stable Diffusion, eller andra modeller. Workflowet är modulärt.

**Q: Fungerar det på andra språk?**
> Ja, men för bäst resultat byt då till en Whisper-modell tränad på det språket. KBLab är specifikt för svenska.

**Q: Hur snabbt är det?**
> - Whisper transkribering: ~1-2 sekunder
> - Prompt enhancement: ~0.5 sekunder (free tier)
> - Image generation: ~10-15 sekunder (paid tier)
> - **Total**: ~15-20 sekunder från röst till bild

**Q: Kan man köra allt lokalt utan API-nycklar?**
> Ja! Byt ut Gemini mot:
> - Prompt: Local LLM (Ollama, LM Studio)
> - Bild: Stable Diffusion Web UI (AUTOMATIC1111)

## 📊 Technical Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
│  ┌────────────────┐         ┌─────────────────┐            │
│  │ Python Mode    │         │  n8n Mode       │            │
│  │ (WebSocket)    │         │  (HTTP)         │            │
│  └────────┬───────┘         └────────┬────────┘            │
└───────────┼──────────────────────────┼──────────────────────┘
            │                          │
            ▼                          ▼
┌─────────────────────────────────────────────────────────────┐
│               Python FastAPI Server (port 8000)             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  KBLab Whisper (kb-whisper-large)                    │  │
│  │  - Endpoints: /api/transcribe/audio, /text           │  │
│  │  - Model loaded once, shared by both modes           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
            │                          │
            │                          ▼
            │              ┌────────────────────────┐
            │              │  n8n Workflow Engine   │
            │              │  (port 5678)           │
            │              │                        │
            │              │  - Voice Detection     │
            │              │  - Gemini Free API     │
            │              │  - Gemini Paid API     │
            │              │  - Image Processing    │
            │              └────────────────────────┘
            │                          │
            ▼                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Google Gemini APIs                          │
│  ┌─────────────────────┐   ┌──────────────────────┐        │
│  │ Free Tier           │   │ Paid Tier            │        │
│  │ gemini-2.0-flash    │   │ gemini-2.5-flash-img │        │
│  │ (Text enhancement)  │   │ (Image generation)   │        │
│  └─────────────────────┘   └──────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 🎓 Key Takeaways for Audience

1. **AI Agents = Workflows**: Not just chatbots, but automated processes
2. **Local First**: Whisper runs locally, only cloud for heavy lifting
3. **Cost Optimization**: Strategic use of free/paid tiers
4. **Swedish Language**: Importance of language-specific models
5. **Modular Design**: Easy to swap components (Whisper → other, Gemini → other)
6. **n8n Power**: Visual workflow creation without heavy coding

## 📦 Post-Demo Resources

**GitHub Repo:** (Your repo URL here)

**Key Files to Share:**
- `n8n-demo-workflow-presentation.json` - Import-ready workflow
- `DEMO_PRESENTATION_GUIDE.md` - Full walkthrough
- `requirements.txt` - Python dependencies

**Follow-up Steps for Attendees:**
1. Install n8n: `npm install -g n8n`
2. Get Gemini API keys: https://aistudio.google.com/apikey
3. Clone repo and run `pip install -r requirements.txt`
4. Import workflow and start creating!

---

**Good luck with your presentation! 🎉**
