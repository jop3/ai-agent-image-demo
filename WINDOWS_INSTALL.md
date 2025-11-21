# 🪟 Windows Installation Guide

## Problem: PyAV (av) installation failure

`faster-whisper` kräver `av` paketet som behöver kompileras på Windows, vilket orsakar fel.

## ✅ Lösning 1: Använd pre-built wheel (REKOMMENDERAT)

**Steg 1:** Installera PyAV separat från pre-built wheel:

```powershell
# Installera PyAV från conda-forge (enklast)
pip install av --only-binary av --extra-index-url https://pypi.anaconda.org/scientific-python-nightly-wheels/simple
```

Om det inte fungerar, prova:

```powershell
# Alternativt: Ladda ner pre-built wheel från GitHub Releases
# Gå till: https://github.com/PyAV-Org/PyAV/releases
# Ladda ner rätt .whl för din Python-version (cp313 = Python 3.13)
# Exempel:
pip install PyAV-12.3.0-cp313-cp313-win_amd64.whl
```

**Steg 2:** Installera resten av dependencies:

```powershell
pip install -r requirements.txt
```

## ✅ Lösning 2: Använd Conda (om du har Anaconda/Miniconda)

```powershell
conda install -c conda-forge av
pip install -r requirements.txt
```

## ✅ Lösning 3: Installera FFmpeg + Build Tools (avancerat)

**Steg 1:** Installera FFmpeg:

```powershell
# Med Chocolatey:
choco install ffmpeg

# Eller ladda ner manuellt från:
# https://www.gyan.dev/ffmpeg/builds/
```

**Steg 2:** Installera Visual Studio Build Tools:

Ladda ner från: https://visualstudio.microsoft.com/downloads/
- Välj "Build Tools for Visual Studio 2022"
- Installera "Desktop development with C++"

**Steg 3:** Installera dependencies:

```powershell
pip install -r requirements.txt
```

## ✅ Lösning 4: Använd WSL2 (Linux på Windows)

Om inget annat fungerar, kör projektet i WSL2:

```bash
# I WSL2 Ubuntu:
sudo apt update
sudo apt install python3-pip ffmpeg
pip install -r requirements.txt
```

## 🆘 Snabb fix för att testa

Om du bara vill testa systemet snabbt, kan du tillfälligt använda CPU-baserad Whisper:

**Ändra i `main.py` rad 51-55:**

```python
# Ändra från CUDA till CPU
self.whisper = WhisperModel(
    WHISPER_MODEL,
    device="cpu",           # ← Ändra från "cuda"
    compute_type="int8"     # ← Ändra från "float16"
)
```

Detta kommer fungera men vara långsammare.

## 📞 Hjälp Behövs?

Om ingen lösning fungerar, skicka följande info:
- Python version: `python --version`
- Pip version: `pip --version`
- OS version: `winver`
- Exakt felmeddelande

## ⚡ Min Rekommendation

**För din föreläsning:**
1. Prova Lösning 1 (pre-built wheel) först
2. Om det inte fungerar: Använd Lösning 2 (Conda)
3. Som sista utväg: CPU-mode för testing

De flesta Windows-användare lyckas med pre-built wheels! 🎉
