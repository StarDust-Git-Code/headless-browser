# ==============================================================================
# Headless Web Tools REST API - Production Dockerfile for Render.com
# ==============================================================================

# Stage 1: Build / Download Stage for Obscura binary
FROM alpine:3.19 AS builder

RUN apk add --no-cache curl tar ca-certificates jq

WORKDIR /tmp

# Dynamically fetch the official v0.2.0 x86_64 Linux rendering+stealth release binary from GitHub Releases
RUN set -eux; \
    ASSET_URL=$(curl -s https://api.github.com/repos/h4ckf0r0day/obscura/releases/tags/v0.2.0 \
      | jq -r '.assets[]? | select(.name | contains("x86_64") and contains("linux") and (contains("no-render") | not)) | .browser_download_url' \
      | head -n 1); \
    if [ -z "$ASSET_URL" ] || [ "$ASSET_URL" = "null" ]; then \
      ASSET_URL="https://github.com/h4ckf0r0day/obscura/releases/download/v0.2.0/obscura-x86_64-unknown-linux-gnu.tar.gz"; \
    fi; \
    echo "Downloading release from: $ASSET_URL"; \
    curl -fsSL "$ASSET_URL" -o obscura.tar.gz; \
    tar -xzf obscura.tar.gz; \
    find . -maxdepth 2 -type f -name obscura -exec mv {} /tmp/obscura \;; \
    chmod +x /tmp/obscura

# Stage 2: Production Python & Obscura Runtime
FROM python:3.10-slim-bookworm AS runner

# Install essential runtime libraries for Obscura and Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl3 \
    fontconfig \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Obscura binary from builder
COPY --from=builder /tmp/obscura /usr/local/bin/obscura

# Copy Python requirements & install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium browser driver
RUN python -m playwright install chromium --with-deps

# Copy application source files
COPY . .

# Environment configuration
ENV HOST=0.0.0.0
ENV PORT=10000
ENV OBSCURA_CDP_URL=ws://127.0.0.1:9222
ENV OBSCURA_NETWORK_BODY_BUFFER_BYTES=104857600

# Expose Render internal routing port
EXPOSE 10000

# Start Obscura local server in background & launch FastAPI on Render's PORT 10000
CMD ["sh", "-c", "obscura serve --host 127.0.0.1 --port 9222 --stealth & uvicorn api:app --host 0.0.0.0 --port 10000"]
