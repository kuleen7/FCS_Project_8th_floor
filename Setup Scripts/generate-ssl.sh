#!/bin/bash

# SSL Certificate Generation Script
# This script generates a self-signed SSL certificate for development

echo "🔒 Generating SSL Certificate for HTTPS..."

# Create ssl directory if it doesn't exist
mkdir -p ssl

# Generate private key and certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=SecureJobPlatform/OU=Development/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"

# Set appropriate permissions
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "✓ SSL certificate generated successfully!"
echo "  Certificate: ssl/cert.pem"
echo "  Private Key: ssl/key.pem"
echo ""
echo "⚠️  Note: This is a self-signed certificate for development only."
echo "    Your browser will show a security warning - this is expected."
echo "    For production, use a certificate from a trusted CA (Let's Encrypt)."
