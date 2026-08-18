# Obscura Headless Browser Engine on Render.com

Production deployment configuration for hosting the [Obscura](https://github.com/h4ckf0r0day/obscura) headless browser engine on [Render.com](https://render.com) with Chrome DevTools Protocol (CDP) WebSocket support.

---

## 📁 Repository Structure

```
├── .gitignore               # Git ignored patterns
├── Dockerfile               # Multi-stage production container definition
├── render.yaml              # Render Blueprint Infrastructure-as-Code
├── verify_connection.py     # Playwright connection test script (async CDP over WSS)
└── README.md                # Deployment and setup guide
```

---

## 🚀 Quick Deployment Guide

### 1. Initialize Git & Push to GitHub

Run these commands in your project root:

```bash
# 1. Initialize Git
git init

# 2. Stage files
git add .

# 3. Create initial commit
git commit -m "feat: Add Obscura Render deployment configuration"

# 4. Set branch to main
git branch -M main

# 5. Add remote GitHub repository
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git

# 6. Push to GitHub
git push -u origin main
```

---

### 2. Deploy on Render.com

1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub repository.
4. Render will detect `render.yaml` and configure the Web Service with:
   - **Port**: `10000`
   - **Environment Variables**:
     - `OBSCURA_NETWORK_BODY_BUFFER_BYTES=104857600` (100 MB buffer)
     - `OBSCURA_STEALTH=on`
   - **Plan**: `standard` (recommended for headless browser workloads)
5. Click **Apply**.

---

### 3. Verify Remote Connection

Install Playwright locally:

```bash
pip install playwright
playwright install chromium
```

Run the connection test against your live Render service:

```bash
python verify_connection.py wss://<YOUR_RENDER_SERVICE_NAME>.onrender.com
```
