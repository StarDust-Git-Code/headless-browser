# ==============================================================================
# Obscura Headless Browser Engine - Production Dockerfile for Render.com
# ==============================================================================

# Build / Runtime stage using the official Obscura base image
FROM h4ckf0r0day/obscura:v0.2.0 AS runner

# Set working directory
WORKDIR /app

# Define default environment variables
ENV HOST=0.0.0.0
ENV PORT=10000
ENV OBSCURA_NETWORK_BODY_BUFFER_BYTES=104857600

# Expose Render's internal routing port
EXPOSE 10000

# Set default execution command
ENTRYPOINT ["obscura"]
CMD ["serve", "--host", "0.0.0.0", "--port", "10000", "--stealth", "on"]
