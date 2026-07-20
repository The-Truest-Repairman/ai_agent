#!/usr/bin/bash
# Instrumented remote.sh for ONE diagnostic session. Swap in temporarily:
#   cp ~/remote.sh ~/remote.sh.bak && cp ~/remote-diagnose.sh ~/remote.sh
#   systemctl --user restart cec-bridge.service
# Then: press up, press play (Steam open), press up again.
# Read ~/cec_log.txt — tells us whether loop dies vs ydotool dies vs CEC stops.
# Restore: mv ~/remote.sh.bak ~/remote.sh && systemctl --user restart cec-bridge.service

set -euo pipefail

export YDOTOOL_SOCKET="/run/user/$(id -u)/.ydotool_socket"
LOG="${HOME}/cec_log.txt"

log() { printf '%s %s\n' "$(date -Is)" "$*" >> "$LOG"; }

pgrep ydotoold >/dev/null || ydotoold &
log "DIAG: cec-bridge started pid=$$"

tail -f /dev/null | \
  cec-client -d 8 -t p -o bazzite 2>&1 | \
  stdbuf -oL grep --line-buffered -E '>> (04|0[bB]):44' | \
  while read -r line; do
    log "DIAG: raw $line"
    case "$line" in
      *":44:01"*)
        log "DIAG: up before ydotool ydotoold=$(pgrep -x ydotoold || echo dead)"
        if ydotool key 103:1 103:0 >> "$LOG" 2>&1; then
          log "DIAG: up ydotool OK"
        else
          log "DIAG: up ydotool FAIL rc=$?"
        fi
        ;;
      *":44:44"*)
        log "DIAG: play steam=$(pgrep -x steam || echo absent) ydotoold=$(pgrep -x ydotoold || echo dead)"
        log "DIAG: play running bazzite-steam"
        /usr/bin/bazzite-steam >> "$LOG" 2>&1 &
        sleep 2
        log "DIAG: play after bazzite-steam ydotoold=$(pgrep -x ydotoold || echo dead)"
        if ydotool key 103:1 103:0 >> "$LOG" 2>&1; then
          log "DIAG: play inline ydotool OK"
        else
          log "DIAG: play inline ydotool FAIL rc=$?"
        fi
        ;;
    esac
  done

log "DIAG: loop exited (should never appear if loop is alive)"
