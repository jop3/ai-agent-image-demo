# 🎭 Demo Presentation Guide: Voice-to-Image

En guide för att demonstrera AI Voice-to-Image först i Python och sedan bygga samma sak i n8n.

## 🎯 Demo-struktur

### Del 1: Python-applikationen (15 min)
**Visa den fungerande appen live**

### Del 2: n8n Workflow (20 min)
**Bygg workflowet steg för steg framför publiken**

---

## 📋 Del 1: Python Demo

### Förberedelser (innan presentationen)

1. Starta servern:
```bash
python main.py
```

2. Öppna webbläsaren på: `http://localhost:8000`
3. Ha en backup-bild redo ifall något går fel

### Demo-script

**1. Introduktion (2 min)**
> "Idag ska jag visa er en AI-agent som kan lyssna på svensk röst, förstå vad ni säger, och generera bilder i realtid. Låt mig först visa hur det fungerar."

**2. Live-demonstration (5 min)**

Testa dessa meningar:
1. ✅ **"En vacker solnedgång över havet"** (vänta på paus → auto-generering)
2. ✅ **"En katt som kodar på en dator"** (säg "skapa bild" → röstkommando)
3. ✅ **"AI-agenter som arbetar tillsammans i ett workflow"** (abstrakt koncept)

Efter varje generering:
- Visa den förbättrade prompten
- Peka på hur lång tid det tog
- Förklara vad som händer i bakgrunden

**3. Arkitektur-översikt (3 min)**

Visa koden och förklara flödet:

```
Mikrofon → Whisper (KBLab Swedish) → Detektion → Gemini (prompt) → Gemini (bild)
```

Nämn viktiga delar:
- **KBLab Whisper-large**: 2B parametrar, tränad på 50k+ timmar svensk data
- **Dubbla API-nycklar**: Free tier för text, Paid tier för bilder
- **Smart detektion**: Röstkommandon + meningsavslut

**4. Utmaningar (2 min)**

> "Detta fungerar utmärkt, men vad händer om:
> - Jag inte kan Python?
> - Jag vill integrera med andra system?
> - Jag behöver skala upp eller göra ändringar snabbt?
>
> Låt mig visa er hur vi kan bygga nästan samma sak i n8n - utan att skriva en rad kod."

**5. Övergång till n8n (3 min)**

Öppna n8n och visa det färdiga workflowet (snabbt):
- "Här är samma funktionalitet visualiserad"
- "Varje ruta är ett steg i vår pipeline"
- "Nu ska jag bygga det här från grunden"

---

## 🔨 Del 2: n8n Live-bygge

### Förberedelser

1. Öppna tom n8n-instans: `http://localhost:5678`
2. Ha API-nycklar redo att klistra in
3. Ha test-data förberedd

### Bygge steg-för-steg (bygg live!)

#### Steg 1: Webhook (2 min)

1. Lägg till node: **Webhook**
2. Konfigurera:
   - Method: POST
   - Path: `voice-to-image`
3. Förklara: *"Detta är vår ingång - här tar vi emot data från användaren"*

**Test:**
```bash
curl -X POST http://localhost:5678/webhook/voice-to-image \
  -H "Content-Type: application/json" \
  -d '{"text": "En vacker solnedgång"}'
```

---

#### Steg 2: Whisper Transkribering (3 min)

1. Lägg till node: **Code (JavaScript)**
2. Namnge: **"📝 Whisper Transkribering"**
3. Klistra in kod:

```javascript
const userText = $input.item.json.body.text || $input.item.json.text;

console.log('📝 Input text:', userText);

return {
  json: {
    transcription: userText,
    model_used: 'KBLab/kb-whisper-large'
  }
};
```

4. Förklara:
   - *"I produktion skulle detta vara ett API-anrop till HuggingFace"*
   - *"KBLab/kb-whisper-large är samma modell som Python-versionen"*
   - *"Den är tränad specifikt på svenska"*

**Lägg till note på noden:** "KBLab/kb-whisper-large\nTränad på 50,000+ timmar svensk data"

---

#### Steg 3: Röstkommando-detektion (4 min)

1. Lägg till node: **Code**
2. Namnge: **"🎯 Röstkommando-detektion"**
3. Klistra in kod:

```javascript
const text = $input.item.json.transcription;

const voiceTriggers = [
  'skapa bild',
  'generera bild'
];

let cleanedText = text;
for (const trigger of voiceTriggers) {
  const regex = new RegExp(trigger, 'gi');
  cleanedText = cleanedText.replace(regex, '').trim();
}

return {
  json: {
    original_text: text,
    cleaned_text: cleanedText
  }
};
```

4. Förklara:
   - *"Detta är vår smarta detektion"*
   - *"Vi letar efter 'skapa bild', 'generera bild', osv"*
   - *"Vi tar bort kommandot och behåller bara beskrivningen"*

**Test:** Kör workflowet med `{"text": "En katt skapa bild"}` → Ska bli `"En katt"`

---

#### Steg 4: Prompt-förbättring (5 min)

1. Lägg till node: **HTTP Request**
2. Namnge: **"💡 Förbättra Prompt"**
3. Konfigurera:
   - Method: POST
   - URL: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent`
   - Authentication: Header Auth
   - Header: `x-goog-api-key` = `DIN_FREE_API_KEY`

4. Body (JSON):
```json
{
  "contents": [{
    "parts": [{
      "text": "Du är en expert på att skapa bildprompter.\n\nAnvändaren sa: \"{{$json.cleaned_text}}\"\n\nSkapa en detaljerad bildprompt på engelska.\n\nRegler:\n- Max 2-3 meningar\n- Beskriv färger och stil\n- Svara ENDAST med prompten"
    }]
  }]
}
```

5. Förklara:
   - *"Detta är exakt samma prompt som Python-versionen"*
   - *"Vi använder Free tier för text-generering"*
   - *"Gemini förvandlar 'en katt' till 'A fluffy orange cat sitting on a laptop...'"*

**Lägg till note:** "Gemini 2.0 Flash\nFree Tier"

---

#### Steg 5: Extrahera förbättrad prompt (2 min)

1. Lägg till node: **Code**
2. Namnge: **"📤 Extrahera Prompt"**
3. Kod:

```javascript
const response = $input.item.json;
const enhancedPrompt = response.candidates[0].content.parts[0].text.trim();

return {
  json: {
    enhanced_prompt: enhancedPrompt,
    original_text: $('🎯 Röstkommando-detektion').item.json.original_text
  }
};
```

4. Förklara: *"Gemini svarar i ett komplext format, så vi plockar ut själva texten"*

---

#### Steg 6: Generera bild (4 min)

1. Lägg till node: **HTTP Request**
2. Namnge: **"🎨 Generera Bild"**
3. Konfigurera:
   - Method: POST
   - URL: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent`
   - Authentication: Header Auth
   - Header: `x-goog-api-key` = `DIN_PAID_API_KEY`

4. Body:
```json
{
  "contents": [{
    "parts": [{
      "text": "{{$json.enhanced_prompt}}"
    }]
  }]
}
```

5. **VIKTIGT - Peka ut:**
   - *"Nu använder vi PAID tier API-nyckeln"*
   - *"Endast Paid tier kan generera bilder"*
   - *"Kostar cirka $0.01 per bild"*

**Lägg till note:** "Gemini 2.5 Flash Image\nPaid Tier\n~$0.01/bild"

---

#### Steg 7: Extrahera & Spara bild (2 min)

1. Lägg till node: **Code**
2. Namnge: **"📷 Extrahera Bild"**
3. Kod (förenklad för demo):

```javascript
const response = $input.item.json;
const imageBase64 = response.candidates[0].content.parts[0].inlineData.data;

return {
  json: {
    image_base64: imageBase64,
    enhanced_prompt: $('📤 Extrahera Prompt').item.json.enhanced_prompt
  }
};
```

4. Lägg till node: **Write Binary File** (om du vill spara lokalt)

---

#### Steg 8: Returnera resultat (2 min)

1. Lägg till node: **Respond to Webhook**
2. Konfigurera response:

```json
{
  "type": "image_generated",
  "success": true,
  "image": "{{$json.image_base64}}",
  "prompt": "{{$json.enhanced_prompt}}"
}
```

3. Förklara: *"Nu har vi hela pipelinen! Samma resultat som Python-appen."*

---

## 🎬 Avslutning (3 min)

### Kör live-test

```bash
curl -X POST http://localhost:5678/webhook/voice-to-image \
  -H "Content-Type: application/json" \
  -d '{"text": "En futuristisk stad i solnedgången"}' \
  | jq -r '.image' | base64 -d > demo-image.png
```

Öppna `demo-image.png` → 🎉 **Fungerar!**

### Jämförelse

| Aspekt | Python | n8n |
|--------|--------|-----|
| Setup-tid | 30 min | 10 min |
| Kodrader | 450+ | 0 (visuellt) |
| Debugging | Console logs | Visuell inspektion |
| Integration | Manuell kod | Drag & drop |
| Skalbarhet | Servers + kod | n8n cloud |

### Key Takeaways

> "Samma resultat, två helt olika approacher:
> - **Python**: Full kontroll, perfekt för produktion & komplex logik
> - **n8n**: Snabbt, visuellt, perfekt för prototyper & automation
>
> Båda är rätt - det beror på use case!"

---

## 💡 Tips för presentationen

### Innan du börjar:
1. ✅ Testa Python-appen en gång
2. ✅ Ha API-nycklar i en textfil redo att kopiera
3. ✅ Öppna alla länkar i flikar (HuggingFace, Google AI Studio)
4. ✅ Ha backup-screenshots ifall något kraschar

### Under presentationen:
1. 🎯 Prata långsamt och förklara varje steg
2. 👁️ Visa console-loggar när du testar
3. 🐛 Om något går fel: använd det som lärtillfälle
4. ⏱️ Håll koll på tid - skippa detaljer vid behov

### Efter varje större steg:
- "Frågor hittills?"
- Låt noder köras och visa resultaten
- Peka på vad som händer i UI:n

### Vanliga frågor att förbereda:
**Q: Varför två API-nycklar?**
A: "Gemini Free tier har begränsningar. Bildgenerering kräver Paid tier."

**Q: Kan jag använda andra modeller?**
A: "Absolut! Whisper har många storlekar, och du kan byta till Imagen 3 eller DALL-E."

**Q: Hur hanterar n8n error handling?**
A: "Varje node kan ha error-branches. Vi kan lägga till retry-logik enkelt."

**Q: Kostar n8n något?**
A: "Self-hosted är gratis. Cloud version har betalplaner. Källkoden är öppen."

---

## 📦 Backup-plan

Om något går fel under live-demon:

1. **Python kraschar**: Visa förinspelade screenshots
2. **n8n inte startar**: Visa det färdiga workflowet istället för att bygga
3. **API-fel**: Ha exempel-output JSON förberedd att visa
4. **Inget internet**: Kör lokala modeller (fall back till CPU-version)

---

## 🎁 Bonusmaterial (om tid finns)

### Utvidgningar att visa:
1. **Error handling**: Lägg till en Error Trigger node
2. **Batch processing**: Visa hur man processar flera texter samtidigt
3. **Database**: Spara metadata i SQLite/PostgreSQL node
4. **Notifications**: Skicka till Slack/Discord när bild är klar
5. **Scheduling**: Kör workflowet varje timme med Cron node

---

**Lycka till med presentationen! 🚀**

*Tips: Öva en gång innan den riktiga demon. Timing är allt!*
