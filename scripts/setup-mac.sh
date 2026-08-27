#!/bin/bash
set -e

echo "Setting up local environment via Homebrew..."

# Install required packages
brew install postgresql@16 mongodb-community redis rabbitmq meilisearch keycloak
brew install minio/stable/minio

# Start services
echo "Starting services..."
brew services start postgresql@16
brew services start mongodb-community
brew services start redis
brew services start rabbitmq
brew services start meilisearch

# Note: minio and keycloak might need manual configuration before starting via brew services
echo "Setup complete. Please see README for next steps on starting MinIO and Keycloak."
