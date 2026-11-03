#!/usr/bin/env bash
# Lancé à chaque démarrage du Codespace (postStartCommand).
# 1) démarre le serveur de correction  2) rend le port 8765 public pour le site.
cd "$(dirname "$0")/.."
pkill -f "runner/server.py" 2>/dev/null || true
setsid nohup python runner/server.py > /tmp/kata-runner.log 2>&1 < /dev/null &

for i in $(seq 1 60); do
  curl -s http://localhost:8765/health >/dev/null && break
  sleep 1
done

if [ -n "$CODESPACE_NAME" ]; then
  for i in 1 2 3 4 5; do
    if gh codespace ports visibility 8765:public -c "$CODESPACE_NAME" >> /tmp/kata-runner.log 2>&1; then
      echo "port 8765 public" >> /tmp/kata-runner.log
      break
    fi
    sleep 4
  done
fi
exit 0
