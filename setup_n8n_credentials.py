#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script för att automatiskt lägga till credentials i n8n
Läser API-nycklar från .env och skapar credentials via n8n API
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Ladda .env
load_dotenv()

# n8n konfiguration
N8N_URL = os.getenv("N8N_URL", "http://localhost:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")

# Gemini API Keys från .env
GEMINI_FREE_KEY = os.getenv("GEMINI_API_KEY_FREE")
GEMINI_PAID_KEY = os.getenv("GEMINI_API_KEY_PAID")

def get_credential_types(headers):
    """Hämtar alla tillgängliga credential types från n8n"""
    url = f"{N8N_URL}/types/credentials.json"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            types = response.json()
            # Filter for Google/Gemini related types
            google_types = [t for t in types if 'google' in t.get('name', '').lower() or 'gemini' in t.get('name', '').lower()]
            return google_types
        return []
    except:
        return []

def create_credential(name, credential_data, headers):
    """Skapar en credential i n8n"""
    url = f"{N8N_URL}/api/v1/credentials"

    try:
        response = requests.post(url, json=credential_data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Skapade credential: {name}")
            return response.json()
        elif response.status_code == 409:
            print(f"⚠️  Credential '{name}' finns redan")
            return None
        else:
            print(f"❌ Fel vid skapande av '{name}': {response.status_code}")
            print(f"   Response: {response.text}")

            # Try to get available types
            print(f"   Försöker hitta tillgängliga credential types...")
            types = get_credential_types(headers)
            if types:
                print(f"   Google-relaterade typer:")
                for t in types[:5]:
                    print(f"     - {t.get('name', 'unknown')}")

            return None

    except requests.exceptions.ConnectionError:
        print(f"❌ Kunde inte ansluta till n8n på {N8N_URL}")
        print(f"   Kontrollera att n8n körs: n8n start")
        return None
    except Exception as e:
        print(f"❌ Oväntat fel: {e}")
        return None

def main():
    print("=" * 60)
    print("🔧 n8n Credential Setup (AI Nodes)")
    print("=" * 60)
    print()

    # Kontrollera att API-nycklar finns
    if not GEMINI_FREE_KEY:
        print("❌ GEMINI_API_KEY_FREE saknas i .env")
        return

    if not GEMINI_PAID_KEY:
        print("❌ GEMINI_API_KEY_PAID saknas i .env")
        return

    if not N8N_API_KEY:
        print("⚠️  N8N_API_KEY saknas i .env")
        print()
        print("📋 Följ dessa steg för manuell setup:")
        print()
        print("1. Öppna n8n: http://localhost:5678")
        print("2. Gå till 'Credentials' i sidomenyn")
        print("3. Klicka 'Add Credential' → 'Google Gemini API'")
        print()
        print("Credential 1 (Free Tier):")
        print(f"  Name: Google Gemini Free")
        print(f"  API Key: {GEMINI_FREE_KEY}")
        print()
        print("Credential 2 (Paid Tier):")
        print(f"  Name: Google Gemini Paid")
        print(f"  API Key: {GEMINI_PAID_KEY}")
        print()
        return

    print(f"📍 n8n URL: {N8N_URL}")
    print(f"🔑 Gemini Free Key: {GEMINI_FREE_KEY[:20]}...")
    print(f"🔑 Gemini Paid Key: {GEMINI_PAID_KEY[:20]}...")
    print(f"🔐 n8n API Key: {N8N_API_KEY[:20]}...")
    print()

    # Headers för API-anrop
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-N8N-API-KEY": N8N_API_KEY
    }

    print("📝 Skapar credentials för AI nodes...")
    print()

    # For AI nodes, we need to use googleGeminiOAuth2Api or just stick with HTTP header auth
    # Since we have API keys, let's create simple HTTP header auth that works everywhere

    # Credential 1: Google Gemini API (Free Tier) - HTTP Header Auth
    free_credential = {
        "name": "Google Gemini Free",
        "type": "httpHeaderAuth",
        "data": {
            "name": "x-goog-api-key",
            "value": GEMINI_FREE_KEY
        }
    }

    # Credential 2: Google Gemini API (Paid Tier) - HTTP Header Auth
    paid_credential = {
        "name": "Google Gemini Paid",
        "type": "httpHeaderAuth",
        "data": {
            "name": "x-goog-api-key",
            "value": GEMINI_PAID_KEY
        }
    }

    # Skapa credentials
    create_credential("Google Gemini Free", free_credential, headers)
    create_credential("Google Gemini Paid", paid_credential, headers)

    print()
    print("⚠️  OBS! AI nodes kräver OAuth2 eller specifika credential typer.")
    print("   Dessa HTTP header credentials fungerar för HTTP Request nodes.")
    print()
    print("   För AI nodes, konfigurera credentials manuellt i n8n UI:")
    print("   1. Gå till Credentials → Add Credential")
    print("   2. Sök efter 'Google' och välj lämplig typ")
    print("   3. Följ instruktionerna för att koppla ditt Google-konto")

    print()
    print("=" * 60)
    print("✅ Setup klar!")
    print()
    print("📋 Rekommendation:")
    print("   Använd 'n8n-demo-workflow-presentation.json' (HTTP Request version)")
    print("   Detta fungerar direkt med de skapade credentials!")
    print()
    print("📋 Nästa steg:")
    print("1. Öppna n8n: http://localhost:5678")
    print("2. Importera workflow: n8n-demo-workflow-presentation.json")
    print("3. Välj credentials i varje HTTP Request node")
    print("4. Kör workflow!")
    print()
    print("💡 AI nodes kräver OAuth2-setup vilket är mer komplext.")
    print("   HTTP Request nodes fungerar lika bra för din presentation!")
    print("=" * 60)

if __name__ == "__main__":
    main()
