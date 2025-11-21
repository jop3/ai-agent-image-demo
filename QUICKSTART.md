# 🚀 Quickstart Guide

Kom igång på 5 minuter!

## 1️⃣ Installation (första gången)

```bash
# Installera Python-dependencies
pip install -r requirements.txt

# Kopiera konfigurationsfil
copy .env.example .env
```

## 2️⃣ API-nyckel

1. Gå till: https://aistudio.google.com/app/apikey
2. Logga in med Google
3. Skapa ny API-nyckel
4. Öppna `.env` och klistra in nyckeln:

```
GEMINI_API_KEY=din_nyckel_här
```

## 3️⃣ Testa installationen

```bash
python test_setup.py
```

Alla tester ska vara gröna ✅

## 4️⃣ Kör programmet

**Enklaste sättet (Windows):**

Dubbelklicka på `start.bat`

**Manuellt:**

Terminal 1:
```bash
python main.py
```

Terminal 2:
```bash
python server.py
```

## 5️⃣ Använd!

1. Öppna webbläsaren på: **http://localhost:8000**
2. Klicka "Starta Inspelning"
3. Ge mikrofon-behörighet
4. **Börja prata!**

## 💡 Tips för bästa resultat

- Prata **tydligt** och naturligt
- Avsluta meningar med en **liten paus**
- Systemet känner automatiskt när du är färdig
- Ju mer beskrivande du är, desto bättre blir bilden!

## 🎬 Exempel på meningar

> "En robot som sitter vid ett skrivbord och programmerar"

> "En futuristisk stad med flygande bilar"

> "En AI-agent som ett workflow-diagram med smarta beslutspunkter"

> "En solnedgång över havet i akvarellstil"

## ⚙️ Snabbjusteringar

### Bildkvalitet vs Hastighet

Ändra i `.env`:

```bash
# Snabbast (gratis)
IMAGE_MODEL=gemini-2.5-flash-image

# Högsta kvalitet (kostar)
IMAGE_MODEL=imagen-4.0-generate-001
```

### Känslighet

```bash
# Kortare paus = snabbare triggar
SILENCE_DURATION=1.0

# Längre paus = mer tid att prata
SILENCE_DURATION=2.0
```

## 🐛 Problem?

### "Kunde inte ladda Whisper"
→ Kontrollera CUDA: `nvidia-smi`

### "Kunde inte få tillgång till mikrofonen"
→ Kolla behörigheter i Chrome/Edge

### "API error"
→ Kontrollera API-nyckel i `.env`

### "Ingen bild genereras"
→ Titta i backend-terminalfönstret för felmeddelanden

## 📞 Mer hjälp

Se `README.md` för fullständig dokumentation!

---

**Lycka till med din föreläsning!** 🎤🎨
