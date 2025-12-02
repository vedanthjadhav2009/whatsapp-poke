# OpenPoke WhatsApp Deployment Guide

Complete guide to deploy OpenPoke with WhatsApp integration using Railway and YCloud.

---

## Prerequisites

- [Railway account](https://railway.app) (free tier works)
- [YCloud account](https://www.ycloud.com) with WhatsApp Business API access
- Your existing API keys (Ananas AI, Composio)

---

## Part 1: Deploy to Railway

### Step 1: Push Code to GitHub

If not already on GitHub:
```bash
git add .
git commit -m "Add WhatsApp integration"
git remote add origin https://github.com/YOUR_USERNAME/whatsapp-poke.git
git push -u origin main
```

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select your `whatsapp-poke` repository
6. Railway will automatically detect Python and start deploying

### Step 3: Add Environment Variables

In Railway Dashboard → Your Project → **Variables** tab, add these:

```env
# Required: AI & Email
ANANNAS_API_KEY=your_anannas_api_key
COMPOSIO_API_KEY=your_composio_api_key
COMPOSIO_GMAIL_AUTH_CONFIG_ID=your_gmail_auth_config_id

# Required: YCloud WhatsApp (fill YCLOUD_WEBHOOK_SECRET after Part 2)
YCLOUD_API_KEY=your_ycloud_api_key
YCLOUD_PHONE_NUMBER=+1234567890

# Leave empty for now - will fill after creating webhook in YCloud
YCLOUD_WEBHOOK_SECRET=
```

### Step 4: Generate Public URL

1. In Railway Dashboard → Your Project → **Settings**
2. Go to **Networking** section
3. Click **"Generate Domain"**
4. You'll get a URL like: `https://whatsapp-poke-production.up.railway.app`
5. **Save this URL** - you'll need it for YCloud webhook setup

### Step 5: Verify Deployment

1. Wait for deployment to complete (check **Deployments** tab)
2. Visit: `https://YOUR-RAILWAY-URL/api/v1/whatsapp/health`
3. You should see: `{"status":"not_configured","configured":false}` (expected until webhook secret is set)

---

## Part 2: Configure YCloud WhatsApp

### Step 1: Get YCloud API Key

1. Log in to [YCloud Console](https://www.ycloud.com/console)
2. Go to **Developers** → **API Keys**
3. Create a new API key or copy existing one
4. Add to Railway: `YCLOUD_API_KEY=your_key`

### Step 2: Get Your WhatsApp Business Phone Number

1. In YCloud Console → **WhatsApp Manager** → **Phone Numbers**
2. If you don't have one, complete the **Embedded Signup** flow
3. Copy your phone number in international format (e.g., `+14155551234`)
4. Add to Railway: `YCLOUD_PHONE_NUMBER=+14155551234`

### Step 3: Create Webhook Endpoint

1. In YCloud Console → **Developers** → **Webhooks**
2. Click **"Create Endpoint"**
3. Fill in:
   - **URL**: `https://YOUR-RAILWAY-URL/api/v1/whatsapp/webhook`
   - **Description**: `OpenPoke WhatsApp Bot`
   - **Enabled Events**: Select `whatsapp.inbound_message.received`
   - **Status**: `Active`
4. Click **Create**

### Step 4: Copy Webhook Secret

1. After creating the webhook, you'll see a **secret** value
2. It looks like: `whsec_a1b2c3d4e5f6g7h8i9j0...`
3. **Copy this secret**

### Step 5: Add Webhook Secret to Railway

1. Go to Railway Dashboard → Your Project → **Variables**
2. Add: `YCLOUD_WEBHOOK_SECRET=whsec_your_secret_here`
3. Railway will automatically redeploy

### Step 6: Verify Full Setup

1. Visit: `https://YOUR-RAILWAY-URL/api/v1/whatsapp/health`
2. You should now see: `{"status":"ok","configured":true}`

---

## Part 3: Test Your Bot

### Send a Test Message

1. Open WhatsApp on your phone
2. Add your YCloud business phone number as a contact
3. Send a message like: "Hello!"
4. You should receive a response from OpenPoke within a few seconds

### Check Logs (if issues)

In Railway Dashboard → Your Project → **Deployments** → Click latest deployment → **View Logs**

Look for:
- `Received WhatsApp message` - confirms webhook is working
- `Sending WhatsApp message` - confirms response is being sent
- Any error messages

---

## Troubleshooting

### "status": "not_configured"
- Check all three YCloud environment variables are set in Railway
- Redeploy if you just added them

### Messages not received
- Verify webhook URL is exactly: `https://YOUR-URL/api/v1/whatsapp/webhook`
- Check webhook is set to `Active` in YCloud
- Ensure `whatsapp.inbound_message.received` event is enabled

### Messages received but no response
- Check Railway logs for errors
- Verify `ANANNAS_API_KEY` is valid
- Check the interaction agent is processing correctly

### "Invalid signature" errors
- Verify `YCLOUD_WEBHOOK_SECRET` matches exactly what YCloud shows
- Make sure there are no extra spaces when copying

### 24-hour window expired
- WhatsApp requires users to message first within 24 hours
- If no recent message from user, you'll need template messages (not implemented yet)

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `ANANNAS_API_KEY` | Yes | Ananas AI API key for LLM |
| `COMPOSIO_API_KEY` | Yes | Composio API key |
| `COMPOSIO_GMAIL_AUTH_CONFIG_ID` | Yes | Gmail auth config from Composio |
| `YCLOUD_API_KEY` | Yes | YCloud API key |
| `YCLOUD_PHONE_NUMBER` | Yes | Your WhatsApp Business number (+1234567890) |
| `YCLOUD_WEBHOOK_SECRET` | Yes | Webhook secret from YCloud |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/whatsapp/webhook` | POST | YCloud webhook receiver |
| `/api/v1/whatsapp/health` | GET | Health check for WhatsApp integration |

---

## Next Steps

Once working, you can:
1. **Custom domain**: Add your own domain in Railway settings
2. **Template messages**: Create YCloud templates for proactive messaging
3. **Media support**: Extend to handle images, documents (future enhancement)
