#!/usr/bin/env bash
set -e

echo "=========================================="
echo "    NutriPlan Local LLM Setup (Ollama)    "
echo "=========================================="

if ! command -v ollama &> /dev/null
then
    echo "[!] Ollama could not be found. Installing via Homebrew..."
    brew install --cask ollama
else
    echo "[✓] Ollama is already installed."
fi

echo "[*] Starting Ollama server in the background..."
# This might fail if the app is already running, which is fine
open -a Ollama || true

echo "[*] Waiting for Ollama API to be ready on port 11434..."
until curl -s -f -o /dev/null "http://localhost:11434/api/tags"
do
  sleep 2
done

echo "[*] Pulling Llama 3 model (this may take a few minutes depending on your internet connection)..."
ollama pull llama3

echo "=========================================="
echo "[✓] Ollama and Llama 3 are ready for Generative Meal Planning!"
echo "=========================================="
