#!/usr/bin/env sh
set -eu

CERT_DIR="${1:-ops/certs}"
HOST="${2:-localhost}"

mkdir -p "$CERT_DIR"

openssl req \
  -x509 \
  -nodes \
  -newkey rsa:2048 \
  -days 365 \
  -keyout "$CERT_DIR/privkey.pem" \
  -out "$CERT_DIR/fullchain.pem" \
  -subj "/CN=$HOST" \
  -addext "subjectAltName=DNS:$HOST,DNS:localhost,IP:127.0.0.1"

chmod 600 "$CERT_DIR/privkey.pem"
printf 'Generated development TLS certificate for %s in %s\n' "$HOST" "$CERT_DIR"
