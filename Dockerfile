# Use official Puppeteer image with Chrome pre-installed
FROM ghcr.io/puppeteer/puppeteer:21.5.2

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies with optimizations for Cloud Run
RUN npm ci --only=production --no-audit --no-fund

# Copy application code
COPY server.js ./

# Set environment variables for Google Cloud Run
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome-stable
ENV NODE_ENV=production

# Create non-root user for security
RUN groupadd -r pptruser && useradd -r -g pptruser -G audio,video pptruser \
    && mkdir -p /home/pptruser/Downloads \
    && chown -R pptruser:pptruser /home/pptruser \
    && chown -R pptruser:pptruser /app

# Switch to non-root user
USER pptruser

# Expose port (Google Cloud Run uses PORT environment variable)
EXPOSE 8080

# Start the application
CMD ["node", "server.js"]
