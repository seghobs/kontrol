#!/usr/bin/env bash

set -euo pipefail

REPO_URL="${1:-https://github.com/seghobs/kontrol.git}"
TARGET_DIR="${2:-kontrol}"

if [ -e "$TARGET_DIR" ]; then
  echo "Hata: '$TARGET_DIR' zaten var. Bos bir klasor adi verin."
  exit 1
fi

echo "Proje indiriliyor: $REPO_URL"
git clone "$REPO_URL" "$TARGET_DIR"

echo "Yazma/okuma izinleri veriliyor..."
chmod -R u+rwX "$TARGET_DIR"

if [ -f "$TARGET_DIR/app.db" ]; then
  chmod u+rw "$TARGET_DIR/app.db"
fi

echo "Tamamlandi. Proje '$TARGET_DIR' klasorune indirildi ve izinler ayarlandi."
echo "Not: Script uygulamayi calistirmaz."
