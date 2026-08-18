# ==============================================================================
# Obscura Headless Browser Engine - Production Dockerfile for Render.com
# ==============================================================================

# Stage 1: Build / Download Stage
FROM alpine:3.19 AS builder

RUN apk add --no-cache curl tar ca-certificates jq

WORKDIR /tmp

# Dynamically fetch the official v0.2.0 x86_64 Linux release binary from GitHub Releases
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

# Stage 2: Lightweight Production Runtime
FROM debian:bookworm-slim AS runner

# Install essential runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl3 \
    fontconfig \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy binary from builder
COPY --from=builder /tmp/obscura /usr/local/bin/obscura

# Define default environment variables
ENV HOST=0.0.0.0
ENV PORT=10000
ENV OBSCURA_NETWORK_BODY_BUFFER_BYTES=104857600

# Expose Render's internal routing port
EXPOSE 10000

# Set default execution command
ENTRYPOINT ["obscura"]
CMD ["serve", "--host", "0.0.0.0", "--port", "10000", "--stealth"]
