#!/usr/bin/bash
set -euo pipefail

export YDOTOOL_SOCKET="/run/user/$(id -u)/.ydotool_socket"
LOG="${HOME}/cec_log.txt"
last_play_launch=0

log() { printf '%s %s\n' "$(date -Is)" "$*" >> "$LOG"; }

pgrep ydotoold >/dev/null || ydotoold &
log "CEC bridge: follow TV routing (0b Intel + 04 bazzite)"

tail -f /dev/null | \
  cec-client -d 8 -t p -o bazzite 2>&1 | \
  stdbuf -oL grep --line-buffered -E '>> (04|0[bB]):44' | \
  while read -r line; do
    case "$line" in
      *":44:00"*) ydotool key 28:1 28:0 ;;
      *":44:01"*) ydotool key 103:1 103:0 ;;
      *":44:02"*) ydotool key 108:1 108:0 ;;
      *":44:03"*) ydotool key 105:1 105:0 ;;
      *":44:04"*) ydotool key 106:1 106:0 ;;
      *":44:0d"*) ydotool key 1:1 1:0 ;;
      *":44:44"*)
        now=$(date +%s)
        if ! pgrep -x steam >/dev/null && (( now - last_play_launch >= 3 )); then
          last_play_launch=$now
          log "play: starting steam-bigpicture"
          systemctl --user start steam-bigpicture.service
        fi
        ;;
    esac
  done
