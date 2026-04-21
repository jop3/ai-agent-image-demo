# 🔑 n8n Credentials Setup Guide

Det finns **3 sätt** att lägga till credentials i n8n. Välj den metod som passar dig bäst!

---

## ⚡ Metod 1: Automatiskt via Python-script (SNABBAST)

### Steg 1: Starta n8n

```bash
n8n start
```

### Steg 2: Kör setup-scriptet

```bash
python setup_n8n_credentials.py
```

**Output:**
```
🔧 n8n Credential Setup
================================================================
📍 n8n URL: http://localhost:5678
🔑 Gemini Free Key: [REDACTED - rotate this key]
🔑 Gemini Paid Key: [REDACTED - rotate this key]

📝 Skapar credentials...

✅ Skapade credential: Gemini Free API Key
✅ Skapade credential: Gemini Paid API Key

✅ Setup klar!
```

### Steg 3: Koppla credentials till noder

1. Öppna n8n: `http://localhost:5678`
2. Öppna workflowet
3. Klicka på noden **"💡 Förbättra Prompt (Free)"**
4. Under "Credential to connect with", välj **"Gemini Free API Key"** från dropdown
5. Klicka på noden **"🎨 Generera Bild (Paid)"**
6. Under "Credential to connect with", välj **"Gemini Paid API Key"** från dropdown
7. Spara workflowet

**Klart! 🎉**

---

## 🖱️ Metod 2: Manuellt via n8n UI (REKOMMENDERAT för demo)

Detta är bäst för din presentation eftersom du kan visa processen!

### Steg 1: Öppna Credentials-sidan

1. Öppna n8n: `http://localhost:5678`
2. Klicka på **"Credentials"** i sidomenyn (🔑 ikon)
3. Klicka på **"Add Credential"**

### Steg 2: Skapa "Gemini Free API Key"

1. Sök efter och välj: **"HTTP Header Auth"**
2. Fyll i:
   ```
   Credential Name: Gemini Free API Key
   Name: x-goog-api-key
   Value: [Klistra in GEMINI_API_KEY_FREE från .env]
   ```
3. Klicka **"Save"**

### Steg 3: Skapa "Gemini Paid API Key"

1. Klicka **"Add Credential"** igen
2. Välj: **"HTTP Header Auth"**
3. Fyll i:
   ```
   Credential Name: Gemini Paid API Key
   Name: x-goog-api-key
   Value: [Klistra in GEMINI_API_KEY_PAID från .env]
   ```
4. Klicka **"Save"**

### Steg 4: Koppla till workflowet

1. Öppna ditt workflow
2. Klicka på noden **"💡 Förbättra Prompt (Free)"**
3. Under "Credential for HTTP Header Auth":
   - Klicka dropdown
   - Välj **"Gemini Free API Key"**
4. Klicka på noden **"🎨 Generera Bild (Paid)"**
5. Under "Credential for HTTP Header Auth":
   - Klicka dropdown
   - Välj **"Gemini Paid API Key"**
6. Klicka **"Save"** uppe till höger

**Klart! 🎉**

---

## 📝 Metod 3: Direkt i workflow-noderna (SNABBAST under demo)

Om du bygger workflowet live under demon:

### I noden "💡 Förbättra Prompt (Free)":

1. Under "Authentication", välj **"Generic Credential Type"**
2. Under "Generic Auth Type", välj **"HTTP Header Auth"**
3. Klicka **"Create New Credential"**
4. Fyll i:
   ```
   Credential Name: Gemini Free API Key
   Name: x-goog-api-key
   Value: [YOUR_GEMINI_FREE_API_KEY]
   ```
5. Klicka **"Save"**

### I noden "🎨 Generera Bild (Paid)":

1. Under "Authentication", välj **"Generic Credential Type"**
2. Under "Generic Auth Type", välj **"HTTP Header Auth"**
3. Klicka **"Create New Credential"**
4. Fyll i:
   ```
   Credential Name: Gemini Paid API Key
   Name: x-goog-api-key
   Value: [YOUR_GEMINI_PAID_API_KEY]
   ```
5. Klicka **"Save"**

**Klart! 🎉**

---

## 🧪 Testa att credentials fungerar

### Test 1: I n8n UI

1. Gå till "Credentials" → Hitta "Gemini Free API Key"
2. Klicka på de tre prickarna → "Test Credential"
3. n8n försöker göra ett test-anrop
4. Om du ser ✅ → Fungerar!

### Test 2: Kör workflowet

1. Öppna workflowet
2. Klicka på **"Execute Workflow"**
3. Mata in test-data:
   ```json
   {
     "text": "En vacker solnedgång"
   }
   ```
4. Om alla noder blir gröna ✅ → Credentials fungerar!

### Test 3: Manuell curl

```bash
# Testa Free tier
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: DIN_FREE_KEY" \
  -d '{"contents":[{"parts":[{"text":"Hej!"}]}]}'

# Testa Paid tier
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: DIN_PAID_KEY" \
  -d '{"contents":[{"parts":[{"text":"A cat"}]}]}'
```

---

## 🔒 Säkerhet

### Viktigt att veta:

1. **Credentials lagras krypterat** i n8n's databas
2. **Aldrig i JSON-filen** - därför måste du lägga till dem manuellt
3. **Synliga i UI** - om någon har tillgång till din n8n
4. **Kan delas** mellan workflows
5. **Exporteras INTE** när du exporterar workflow

### Bästa praxis:

- ✅ Använd miljövariabler i produktion
- ✅ Sätt upp n8n authentication om du exponerar externt
- ✅ Använd separate API-nycklar för dev/prod
- ❌ Commit aldrig n8n database-filen till git
- ❌ Dela inte credentials via chat/email

---

## 🐛 Felsökning

### Problem: "Credential not found"

**Lösning:**
1. Gå till "Credentials" i sidomenyn
2. Kontrollera att båda credentials finns
3. Öppna varje node och välj credential från dropdown igen

### Problem: "Authentication failed"

**Möjliga orsaker:**
1. **Fel API-nyckel** - kopiera från .env igen
2. **Free/Paid fel** - kontrollera att du använder rätt nyckel för rätt node
3. **Utgången nyckel** - skapa ny på Google AI Studio

**Test:**
```bash
# Hämta dina nycklar från .env
cat .env | grep GEMINI

# Testa direkt:
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent \
  -H "x-goog-api-key: DIN_NYCKEL" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}'
```

### Problem: "Cannot connect to n8n API"

**Om setup_n8n_credentials.py inte fungerar:**

1. Kontrollera att n8n körs: `curl http://localhost:5678`
2. Kontrollera N8N_URL i .env: `N8N_URL=http://localhost:5678`
3. Om n8n kräver API-key:
   - Generera i n8n: Settings → API
   - Lägg till i .env: `N8N_API_KEY=din_api_key`

---

## 📊 Översikt: Vilka credentials behövs?

| Credential | Node | API Key | Tier | Kostnad |
|-----------|------|---------|------|---------|
| **Gemini Free API Key** | 💡 Förbättra Prompt | GEMINI_API_KEY_FREE | Free | Gratis |
| **Gemini Paid API Key** | 🎨 Generera Bild | GEMINI_API_KEY_PAID | Paid | ~$0.01/bild |

---

## 💡 Tips för presentation

Under demon kan du visa credential-processen för att förklara hur n8n hanterar säkerhet:

1. **Visa Credentials-sidan**
   > "Här lagrar n8n alla API-nycklar krypterat"

2. **Skapa en credential live**
   > "Jag behöver bara göra detta en gång, sedan kan jag återanvända i alla workflows"

3. **Välj från dropdown**
   > "Nu kan jag enkelt välja vilken nyckel varje node ska använda"

4. **Förklara Free vs Paid**
   > "Vi använder Free tier för text-generering, men Paid tier krävs för bilder"

---

## 🎯 Snabb-checklista

Före demon:
- [ ] n8n startat (`n8n start`)
- [ ] Kört `python setup_n8n_credentials.py` ELLER
- [ ] Skapat credentials manuellt i UI
- [ ] Importerat workflow
- [ ] Valt rätt credentials i båda HTTP Request-noder
- [ ] Testat att köra workflowet en gång
- [ ] Verifierat att bild genereras

**Nu är du redo! 🚀**

---

**Pro-tip:** Öva credential-steget en gång innan demon så det går smidigt!
