# 🤖 n8n AI Nodes Setup Guide

## Why Use AI Nodes Instead of HTTP Requests?

### ✅ Benefits of AI Nodes:
1. **Visual Clarity**: AI nodes show with special icons and colors in the workflow
2. **Easier Configuration**: No need to manually construct HTTP requests
3. **Better Error Handling**: Built-in retry logic and error messages
4. **Credential Management**: Centralized API key management
5. **Demo Impact**: Much more impressive to show "AI-powered workflow" with native AI nodes

### Comparison:

**Old Way (HTTP Request):**
```
Generic HTTP Request → Manual JSON construction → Extract response
```

**New Way (AI Nodes):**
```
Google Gemini AI Node → Automatic handling → Clean output
```

---

## 📋 Prerequisites

1. **n8n installed** (version 1.0+ with AI node support)
2. **Google Gemini API Key(s)**
   - Get from: https://aistudio.google.com/apikey
   - You need TWO keys if using free + paid tier strategy:
     - **Free tier key**: For text enhancement (gemini-2.0-flash-exp)
     - **Paid tier key**: For image generation (gemini-2.5-flash-image)
   - OR use one paid tier key for both

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Import the Workflow

1. Open n8n: `http://localhost:5678`
2. Click **"Add workflow"** → **"Import from File"**
3. Select: `n8n-demo-workflow-presentation-ai-nodes.json`
4. Click **"Import"**

### Step 2: Set Up Google Gemini Credentials

#### Option A: Using n8n UI (Recommended)

1. **Open any Gemini node** (click on "💡 4. GEMINI: Förbättra Prompt")

2. **Click on "Credential to connect with"** dropdown

3. **Click "Create New Credential"**

4. **Select credential type:**
   - **For OAuth (Recommended)**: Choose "Google Gemini OAuth2 API"
   - **For API Key**: Choose "Google Gemini API"

5. **Configure based on your choice:**

   **If using OAuth:**
   - Click "Connect my account"
   - Sign in with your Google account
   - Grant permissions
   - Done!

   **If using API Key:**
   - Paste your API key from https://aistudio.google.com/apikey
   - Click "Save"

6. **Repeat for the image generation node** (if using separate keys)
   - Go to "🎨 5. GEMINI: Generera Bild" node
   - If using the same account, select existing credential
   - If using different tier, create new credential with paid tier key

#### Option B: Using Script (Automated)

Create a file `setup_gemini_credentials.py`:

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

N8N_URL = os.getenv('N8N_URL', 'http://localhost:5678')
N8N_API_KEY = os.getenv('N8N_API_KEY')
GEMINI_API_KEY_FREE = os.getenv('GEMINI_API_KEY')
GEMINI_API_KEY_PAID = os.getenv('GEMINI_API_KEY_PAID', GEMINI_API_KEY_FREE)

def create_credential(name, api_key):
    """Create Google Gemini API credential in n8n"""

    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }

    data = {
        "name": name,
        "type": "googleGeminiApi",
        "data": {
            "apiKey": api_key
        }
    }

    response = requests.post(
        f"{N8N_URL}/api/v1/credentials",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        print(f"✅ Created credential: {name}")
        return response.json()
    else:
        print(f"❌ Failed to create {name}: {response.text}")
        return None

if __name__ == "__main__":
    if not N8N_API_KEY:
        print("❌ N8N_API_KEY not found in .env")
        print("📝 Get it from n8n Settings → API → Generate API Key")
        exit(1)

    print("🔧 Setting up Google Gemini credentials...")

    # Create credentials
    create_credential("Google Gemini (Free Tier)", GEMINI_API_KEY_FREE)

    if GEMINI_API_KEY_PAID and GEMINI_API_KEY_PAID != GEMINI_API_KEY_FREE:
        create_credential("Google Gemini (Paid Tier)", GEMINI_API_KEY_PAID)

    print("\n✅ Done! Now open your workflow and select the credentials in each Gemini node.")
```

Run:
```bash
python setup_gemini_credentials.py
```

### Step 3: Update Webhook URL in Frontend

Update `index-n8n.html` (line 269):

```javascript
// OLD:
const N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/voice-to-image';

// NEW (for AI nodes workflow):
const N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/voice-to-image-ai';
```

---

## 🎨 Understanding the AI Nodes

### Node: 💡 4. GEMINI: Förbättra Prompt

**Type:** `@n8n/n8n-nodes-langchain.lmChatGoogleGemini`

**What it does:**
- Takes Swedish text input
- Sends to Gemini 2.0 Flash (free tier)
- Returns enhanced English image prompt

**Configuration:**
```json
{
  "resource": "text",
  "model": "gemini-2.0-flash-exp",
  "prompt": {
    "messages": [
      {
        "role": "user",
        "content": "Du är en expert på bildprompter..."
      }
    ]
  }
}
```

**Output format:**
```json
{
  "message": {
    "content": "A breathtaking sunset over calm waters..."
  }
}
```

### Node: 🎨 5. GEMINI: Generera Bild

**Type:** `@n8n/n8n-nodes-langchain.lmChatGoogleGemini`

**What it does:**
- Takes English prompt
- Sends to Gemini 2.5 Flash Image (paid tier)
- Returns PNG image as binary data

**Configuration:**
```json
{
  "resource": "image",
  "prompt": "{{ $json['🇬🇧 ENGELSK PROMPT'] }}",
  "options": {
    "outputFormat": "image/png"
  }
}
```

**Output format:**
```json
{
  "binary": {
    "data": {
      "data": "base64_encoded_png...",
      "mimeType": "image/png"
    }
  }
}
```

---

## 🧪 Testing the Workflow

### Test 1: Execute Single Node

1. Click on "💡 4. GEMINI: Förbättra Prompt" node
2. Click **"Execute Node"** (in sidebar)
3. Check output - should see enhanced prompt

### Test 2: Full Workflow Test

1. **Activate workflow** (toggle in top-right)
2. **Get webhook URL**: Click on "🎤 1. INPUT: Webhook" → Copy "Test URL"
3. **Send test request**:

```bash
curl -X POST http://localhost:5678/webhook/voice-to-image-ai \
  -H "Content-Type: application/json" \
  -d '{"text": "En vacker solnedgång över havet"}'
```

4. **Check n8n executions** - should see all nodes executed
5. **Check generated_images/** folder - should have new image

---

## 🎯 Presentation Tips with AI Nodes

### Highlight These Points:

1. **"Look, native AI integration!"**
   - Point out the AI node icons
   - Show how n8n has built-in AI capabilities

2. **"No manual API calls needed"**
   - Compare to old HTTP Request version
   - Show cleaner configuration

3. **"Credential management built-in"**
   - Show credentials dropdown
   - Mention centralized key management

4. **"Better error handling"**
   - AI nodes have retry logic
   - Clear error messages

### Demo Flow:

1. **Start at webhook** → Explain input
2. **Whisper node** → Local API call
3. **Detection node** → Voice command logic
4. **PAUSE at first VISA node** → Show data
5. **AI Node #1 (Text)** → "Now watch AI enhance the prompt"
   - Click node → Show configuration
   - Show model selection (Gemini 2.0 Flash)
6. **PAUSE at second VISA node** → Show before/after
7. **AI Node #2 (Image)** → "Now AI generates the image"
   - Click node → Show it's using Gemini Image model
   - Wait for generation
8. **PAUSE at metadata node** → Click "Binary" tab → Show image!
9. **Save node** → Open folder → Show saved file

---

## 🔧 Troubleshooting

### Issue: "Credentials not set"

**Fix:**
1. Click on the red-highlighted node
2. Select credential from dropdown
3. If none exist, create new credential
4. Save workflow

### Issue: "Module @n8n/n8n-nodes-langchain not found"

**Fix:**
Your n8n version doesn't have AI nodes. Update:
```bash
npm update -g n8n
```

### Issue: "Model not available"

**Fix:**
Check your Gemini API key has access to:
- `gemini-2.0-flash-exp` (free tier)
- `gemini-2.5-flash-image` (paid tier)

Go to: https://aistudio.google.com/apikey

### Issue: "Image generation fails"

**Fix:**
1. Check you're using a **paid tier** API key for image generation
2. Check key has credits remaining
3. Try a simpler prompt first

### Issue: "Output format different than expected"

**Fix:**
AI nodes return different structure than HTTP requests:
- **Text output**: `$json.message.content` (not `$json.text`)
- **Binary output**: Same as before (`$binary.data`)

---

## 📊 Cost Comparison

### With AI Nodes (Current Setup):
- **Text Enhancement**: FREE (Gemini 2.0 Flash Exp)
- **Image Generation**: ~$0.01 per image (Gemini 2.5 Flash Image)
- **Total per workflow run**: ~$0.01

### Alternative (All Paid):
- **Text Enhancement**: ~$0.0001 per request (Gemini Pro)
- **Image Generation**: ~$0.01 per image
- **Total per workflow run**: ~$0.0101

**Savings**: 1% with free tier text enhancement (minimal but nice!)

---

## 🎓 Key Takeaways

1. ✅ **AI Nodes** are cleaner and more visual than HTTP requests
2. ✅ **Easier to demonstrate** - audience sees "AI" explicitly
3. ✅ **Better for production** - built-in error handling and retries
4. ✅ **Credential management** - centralized and secure
5. ✅ **Same functionality** - just better packaged!

---

## 📦 Next Steps

After getting this working:

1. **Try other AI nodes:**
   - OpenAI nodes (for DALL-E 3 images)
   - Anthropic Claude nodes (for better text reasoning)
   - Mistral nodes (for local-first approach)

2. **Combine AI nodes:**
   - Use multiple AI models in sequence
   - Compare outputs from different models
   - Create AI agent chains

3. **Add more features:**
   - Image editing with AI
   - Style transfer
   - Multi-language support

---

**Good luck! 🚀**
