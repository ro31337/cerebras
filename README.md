# LiteLLM Proxy: Cerebras → Z.AI Fallback

[По-русски](README-RU.md)

LiteLLM proxy server with automatic fallback from Cerebras to Z.AI when rate limits are exceeded.

## Why This Setup?

We have access to the amazing **GLM-4.6** model, and we have **Cerebras** - an AI chip company that delivers blazing fast inference at **1000 tokens/second**! We also have the regular Z.AI API.

Here's the cool part: **it's the same model** (GLM-4.6) on both platforms. So why not use the super-fast Cerebras requests first, and when we hit the rate limits, **automatically fallback to Z.AI**? This way we get:

- ⚡ **Ultra-fast responses** from Cerebras (1000 tokens/sec!)
- 🔄 **Automatic fallback** to Z.AI when rate limits are hit
- 🚀 **Better performance** than using Z.AI alone

It's like having a turbo button that automatically switches to normal mode when needed. Best of both worlds!

## Setup Instructions

### 1. Install uv

First, install `uv` - a fast Python package installer and resolver written in Rust. It's significantly faster than pip and handles virtual environments seamlessly.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If you want to learn more about uv, read this article: https://emily.space/posts/251023-uv

### 2. Create Virtual Environment

Create a `.venv` directory for isolated Python dependencies:

```bash
uv venv
```

### 3. Activate Virtual Environment

**IMPORTANT:** You need to activate the virtual environment **every time** before running the proxy or tests. This is one of the two essential commands you'll use:

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

Run this **once** after initial setup to install all required packages:

```bash
uv sync
```

### 5. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Now edit `.env` and set your API keys:

#### Get Cerebras API Key (FREE with limits)
1. Go to https://cloud.cerebras.ai/
2. Click the dropdown **"Personal"** in the top navigation
3. Select **"API Keys"**
4. Create or copy your personal API key (free tier with rate limits)

#### Get Z.AI API Key
1. Go to https://z.ai/manage-apikey/apikey-list
2. Create or copy your API key

Your `.env` should look like:
```
CEREBRAS_API_KEY=csk-your-actual-key-here
ZAI_API_KEY=your-actual-zai-key-here
LITELLM_MASTER_KEY=sk-1234
```

## Running the Proxy

Start the proxy server (this is the second essential command):

```bash
./start_proxy.sh
```

You should see output like:

```
Starting LiteLLM proxy server...
Cerebras (primary) → Z.AI GLM-4.6 (fallback)

INFO:     Started server process [78824]
INFO:     Waiting for application startup.

   ██╗     ██╗████████╗███████╗██╗     ██╗     ███╗   ███╗
   ██║     ██║╚══██╔══╝██╔════╝██║     ██║     ████╗ ████║
   ██║     ██║   ██║   █████╗  ██║     ██║     ██╔████╔██║
   ██║     ██║   ██║   ██╔══╝  ██║     ██║     ██║╚██╔╝██║
   ███████╗██║   ██║   ███████╗███████╗███████╗██║ ╚═╝ ██║
   ╚══════╝╚═╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝

LiteLLM: Proxy initialized with Config, Set models:
    glm-4.6
    zai-glm-4.6
    glm-4.5-air
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:4000 (Press CTRL+C to quit)
```

**⚠️ Note:** If port 4000 is already in use, a random port will be selected. Pay attention to the output to see which port is actually being used!

## Test with curl

Test the proxy with a simple request:

```bash
curl -X POST "http://localhost:4000/chat/completions" \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.6",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'
```

## Test Fallback Mechanism

Run 20 parallel requests to trigger Cerebras rate limit and verify automatic fallback to Z.AI:

```bash
source .venv/bin/activate
python test_parallel.py
```

Expected output:
```
✓ Request  1: cerebras/zai-glm-4.6           (3.05s)
✓ Request  2: glm-4-plus                     (4.98s)
✓ Request  3: glm-4-plus                     (4.62s)
...
Cerebras responses: 5
Z.AI responses:     15
Errors:             0

✓✓✓ Fallback to Z.AI IS WORKING! ✓✓✓
```

## Configuration

### Models
- **glm-4.6**: Cerebras (primary, 1000 tok/s, 10 req/min) → Z.AI fallback (for Opus/Sonnet)
- **glm-4.5-air**: Z.AI only, no fallback (for Haiku - fast, cheap tasks)

### Proxy Settings
- **Endpoint**: http://localhost:4000
- **API Key**: sk-1234

## Using with Claude Code

### 1. Configure Claude Code

Configure Claude Code to use this proxy instead of Anthropic's API:

```bash
./configure_claude_env.sh
```

This will set up Claude Code to use:
- **Opus/Sonnet** → glm-4.6 (Cerebras with Z.AI fallback)
- **Haiku** → glm-4.5-air (Z.AI only, for fast tasks)

### 2. Start Proxy and Claude Code

```bash
# Terminal 1: Start the proxy
./start_proxy.sh

# Terminal 2: Start Claude Code
claude
```

### 3. Verify Configuration

After starting Claude Code, verify it's using the local proxy by running:

```
/status
```

You should see:
```
 Version: 2.0.47
 Auth token: ANTHROPIC_AUTH_TOKEN
 Anthropic base URL: http://localhost:4000
 Model: Default (glm-4.6)
```

**✅ If you see `Anthropic base URL: http://localhost:4000`** - perfect! Claude Code is using your local proxy with Cerebras → Z.AI fallback.

**❌ If you see a different URL** - run `./configure_claude_env.sh` again and restart Claude Code.

## Files

- `README.md` - This file (English)
- `README-RU.md` - Russian version
- `config.yaml` - LiteLLM configuration with fallback
- `.env` - API keys for Cerebras and Z.AI
- `.env.example` - Template for environment variables
- `start_proxy.sh` - Start the proxy server
- `configure_claude_env.sh` - Configure Claude Code to use this proxy
- `test_parallel.py` - Test fallback mechanism
- `test_full.py` - Full response test
