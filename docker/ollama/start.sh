#!/bin/bash

set -eu

echo "starting ollama server..."
ollama serve &
ollama_pid=$!

if ! ollama list | grep -q "${OLLAMA_MODEL}"; then
  echo "${OLLAMA_MODEL} model does not exist, downloading..."
  ollama pull "${OLLAMA_MODEL}"
fi

wait ${ollama_pid}
