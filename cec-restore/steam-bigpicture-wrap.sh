#!/usr/bin/bash
# Keeps steam-bigpicture.service alive until the steam binary exits.
# Login shell (-lc) imports DISPLAY / WAYLAND / DBUS from the KDE session.

set -uo pipefail

LOG="${HOME}/steam-bigpicture.log"

log() { printf '%s %s\n' "$(date -Is)" "$*" >> "$LOG"; }

log "starting (wrap pid $$)"
/usr/bin/bash -lc 'exec /usr/bin/bazzite-steam' >> "$LOG" 2>&1 &
launcher_pid=$!

for _ in $(seq 1 90); do
  if pgrep -x steam >/dev/null; then
    break
  fi
  if ! kill -0 "$launcher_pid" 2>/dev/null; then
    wait "$launcher_pid" 2>/dev/null || true
    log "launcher exited before steam appeared"
    exit 1
  fi
  sleep 1
done

if ! pgrep -x steam >/dev/null; then
  log "steam never appeared after 90s"
  exit 1
fi

log "steam running (launcher pid ${launcher_pid})"

while pgrep -x steam >/dev/null; do
  if ! kill -0 "$launcher_pid" 2>/dev/null; then
    log "launcher exited while steam still running"
    exit 1
  fi
  sleep 2
done

wait "$launcher_pid" 2>/dev/null || true
rc=$?
log "steam gone, launcher rc=${rc}"
exit "${rc:-1}"
