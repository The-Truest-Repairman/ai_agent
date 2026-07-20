#!/usr/bin/bash
# CEC play/ydotool diagnostics — run on the NUC with Steam already open.
# Does NOT modify remote.sh. Results go to ~/cec-diagnose.txt
#
# Usage: bash ~/diagnose-play.sh

set -uo pipefail

export YDOTOOL_SOCKET="/run/user/$(id -u)/.ydotool_socket"
LOG="${HOME}/cec-diagnose.txt"
: > "$LOG"

log() { printf '%s %s\n' "$(date -Is)" "$*" | tee -a "$LOG"; }

test_ydotool() {
  local label="$1"
  if ydotool key 103:1 103:0 >> "$LOG" 2>&1; then
    log "${label}: ydotool PASS (rc=0)"
    return 0
  else
    log "${label}: ydotool FAIL (rc=$?)"
    return 1
  fi
}

log "=== env ==="
log "XDG_SESSION_TYPE=${XDG_SESSION_TYPE:-unset}"
log "YDOTOOL_SOCKET=$YDOTOOL_SOCKET"
log "steam=$(pgrep -x steam || echo absent)"
log "ydotoold=$(pgrep -x ydotoold || echo absent)"
log "cec-client=$(pgrep -x cec-client || echo absent)"
log "cec-bridge=$(systemctl --user is-active cec-bridge.service 2>/dev/null || echo unknown)"

log ""
log "=== TEST A: ydotool baseline (Steam running) ==="
pgrep -x ydotoold >/dev/null || ydotoold &
sleep 0.5
test_ydotool "A"

log ""
log "=== TEST B: bazzite-steam while Steam already running ==="
log "B: launching bazzite-steam (same as broken play-focus path)"
/usr/bin/bazzite-steam >> "$LOG" 2>&1 &
sleep 3
test_ydotool "B"
log "B: ydotoold after bazzite-steam=$(pgrep -x ydotoold || echo absent)"

log ""
log "=== TEST C: KWin focus script (no bazzite-steam) ==="
if command -v qdbus6 >/dev/null; then
  qdbus6 org.kde.KWin /Scripting org.kde.kwin.runScript '
for (const w of workspace.windowList()) {
  const cls = w.resourceClass.toLowerCase();
  const cap = w.caption.toLowerCase();
  if (cls.includes("steam") || cap.includes("steam")) { w.activate(); break; }
}
' >> "$LOG" 2>&1 && log "C: qdbus6 focus rc=0" || log "C: qdbus6 focus rc=$?"
else
  log "C: SKIP — qdbus6 not found"
fi
sleep 1
test_ydotool "C"

log ""
log "=== TEST D: set -e + failed ydotool kills piped while loop? ==="
set -euo pipefail
if tail -f /dev/null | head -1 | while read -r _; do
  ydotool key 99999:1 99999:0 2>/dev/null
  log "D: loop iteration survived bad ydotool"
done; then
  log "D: pipeline exit 0 (loop survived)"
else
  log "D: pipeline exit non-zero (loop KILLED by set -e — this explains arrow death)"
fi
set +e

log ""
log "=== TEST E: set -e + good ydotool after simulated failure ==="
set -euo pipefail
if printf '\n' | while read -r _; do
  ydotool key 99999:1 99999:0 2>/dev/null || true
  ydotool key 103:1 103:0 >> "$LOG" 2>&1
  log "E: second ydotool in same loop iteration OK"
done; then
  log "E: || true prevents loop death"
else
  log "E: unexpected pipeline failure"
fi
set +e

log ""
log "=== TEST F: steam window list (for focus matching) ==="
if command -v qdbus6 >/dev/null; then
  qdbus6 org.kde.KWin /Scripting org.kde.kwin.runScript '
for (const w of workspace.windowList()) {
  print(w.resourceClass + " | " + w.caption);
}
' >> "$LOG" 2>&1 || log "F: window list failed rc=$?"
else
  log "F: SKIP — qdbus6 not found"
fi

log ""
log "=== TEST G: steam-bigpicture.service exists? ==="
systemctl --user status steam-bigpicture.service >> "$LOG" 2>&1 || log "G: steam-bigpicture.service not found (expected on your box)"

log ""
log "=== TEST H: app-steam autostart unit ==="
systemctl --user list-units --all --type=service | grep -i steam >> "$LOG" 2>&1 || log "H: no steam units"

log ""
log "=== DONE — paste ~/cec-diagnose.txt ==="
